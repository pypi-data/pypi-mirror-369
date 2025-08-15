import torch
import torch.nn as nn

from edmine.model.module.EmbedLayer import EmbedLayer
from edmine.model.module.PredictorLayer import PredictorLayer
from edmine.model.sequential_kt_model.DLSequentialKTModel import DLSequentialKTModel
from edmine.model.registry import register_model

MODEL_NAME = "qDKT"


@register_model(MODEL_NAME)
class qDKT(nn.Module, DLSequentialKTModel):
    model_name = MODEL_NAME

    def __init__(self, params, objects):
        super(qDKT, self).__init__()
        self.params = params
        self.objects = objects

        model_config = self.params["models_config"][MODEL_NAME]
        embed_config = model_config["embed_config"]
        dim_concept = embed_config["concept"]["dim_item"]
        dim_question = embed_config["question"]["dim_item"]
        dim_correctness = embed_config["correctness"]["dim_item"]
        dim_emb = dim_concept + dim_question + dim_correctness
        dim_latent = model_config["dim_latent"]
        rnn_type = model_config["rnn_type"]
        num_rnn_layer = model_config["num_rnn_layer"]

        self.embed_layer = EmbedLayer(model_config["embed_config"])
        if rnn_type == "rnn":
            self.encoder_layer = nn.RNN(dim_emb, dim_latent, batch_first=True, num_layers=num_rnn_layer)
        elif rnn_type == "lstm":
            self.encoder_layer = nn.LSTM(dim_emb, dim_latent, batch_first=True, num_layers=num_rnn_layer)
        else:
            self.encoder_layer = nn.GRU(dim_emb, dim_latent, batch_first=True, num_layers=num_rnn_layer)
        self.predict_layer = PredictorLayer(model_config["predictor_config"])

    def get_latent(self, batch):
        q2c_transfer_table = self.objects["dataset"]["q2c_transfer_table"]
        q2c_mask_table = self.objects["dataset"]["q2c_mask_table"]

        concept_emb = self.embed_layer.get_emb_fused1(
            "concept", q2c_transfer_table, q2c_mask_table, batch["question_seq"])
        question_emb = self.embed_layer.get_emb("question", batch["question_seq"])
        qc_emb = torch.cat((question_emb, concept_emb), dim=-1)
        correctness_emb = self.embed_layer.get_emb("correctness", batch["correctness_seq"])
        interaction_emb = torch.cat((qc_emb[:, :-1], correctness_emb[:, :-1]), dim=2)

        self.encoder_layer.flatten_parameters()
        latent, _ = self.encoder_layer(interaction_emb)

        return latent

    def forward(self, batch):
        q2c_transfer_table = self.objects["dataset"]["q2c_transfer_table"]
        q2c_mask_table = self.objects["dataset"]["q2c_mask_table"]

        concept_emb = self.embed_layer.get_emb_fused1(
            "concept", q2c_transfer_table, q2c_mask_table, batch["question_seq"])
        question_emb = self.embed_layer.get_emb("question", batch["question_seq"])
        qc_emb = torch.cat((question_emb, concept_emb), dim=-1)

        latent = self.get_latent(batch)

        predict_layer_input = torch.cat((latent, qc_emb[:, 1:]), dim=2)
        predict_score_batch = self.predict_layer(predict_layer_input).squeeze(dim=-1)

        return predict_score_batch

    def get_predict_score(self, batch, seq_start=2):
        mask_seq = torch.ne(batch["mask_seq"], 0)
        # predict_score_batch的shape必须为(bs, seq_len-1)，其中第二维的第一个元素为对序列第二题的预测分数
        # 如此设定是为了做cold start evaluation
        predict_score_batch = self.forward(batch)
        predict_score = torch.masked_select(predict_score_batch[:, seq_start - 2:], mask_seq[:, seq_start - 1:])

        return {
            "predict_score": predict_score,
            "predict_score_batch": predict_score_batch
        }

    def get_predict_score_on_target_question(self, batch, target_index, target_question):
        latent = self.get_latent(batch)
        target_latent = latent[:, target_index - 1]

        q2c_transfer_table = self.objects["dataset"]["q2c_transfer_table"]
        q2c_mask_table = self.objects["dataset"]["q2c_mask_table"]
        target_concept_emb = self.embed_layer.get_emb_fused1(
            "concept", q2c_transfer_table, q2c_mask_table, target_question)
        target_question_emb = self.embed_layer.get_emb("question", target_question)
        target_qc_emb = torch.cat((target_question_emb, target_concept_emb), dim=-1)

        num_question = target_question.shape[1]
        batch_size = batch["correctness_seq"].shape[0]
        target_latent_extend = target_latent.repeat_interleave(num_question, dim=0).view(batch_size, num_question, -1)
        predict_layer_input = torch.cat((target_latent_extend, target_qc_emb), dim=2)
        predict_score = self.predict_layer(predict_layer_input).squeeze(dim=-1)

        return predict_score

    def get_knowledge_state(self, batch, only_last_state=True):
        q2c_transfer_table = self.objects["dataset"]["q2c_transfer_table"]
        q2c_mask_table = self.objects["dataset"]["q2c_mask_table"]
        num_concept = self.params["models_config"][MODEL_NAME]["embed_config"]["concept"]["num_item"]
        dim_question = self.params["models_config"][MODEL_NAME]["embed_config"]["question"]["dim_item"]

        batch_size = batch["correctness_seq"].shape[0]
        first_index = torch.arange(batch_size).long().to(self.params["device"])
        all_concept_id = torch.arange(num_concept).long().to(self.params["device"])
        all_concept_emb = self.embed_layer.get_emb("concept", all_concept_id)

        concept_emb = self.embed_layer.get_emb_fused1(
            "concept", q2c_transfer_table, q2c_mask_table, batch["question_seq"])
        question_emb = self.embed_layer.get_emb("question", batch["question_seq"])
        qc_emb = torch.cat((question_emb, concept_emb), dim=-1)
        correctness_emb = self.embed_layer.get_emb("correctness", batch["correctness_seq"])
        interaction_emb = torch.cat((qc_emb, correctness_emb), dim=2)
        self.encoder_layer.flatten_parameters()
        latent, _ = self.encoder_layer(interaction_emb)
        
        if only_last_state:
            latent = latent[first_index, batch["seq_len"] - 1]
            latent_expanded = latent.repeat_interleave(num_concept, dim=0).view(batch_size, num_concept, -1)
            all_concept_emb_expanded = all_concept_emb.expand(batch_size, -1, -1)
            next_question_emb = torch.zeros((batch_size, num_concept, dim_question)).float().to(self.params["device"])
            predict_layer_input = torch.cat([latent_expanded, all_concept_emb_expanded, next_question_emb], dim=-1)
        else:
            raise NotImplementedError()

        return self.predict_layer(predict_layer_input).squeeze(dim=-1)
