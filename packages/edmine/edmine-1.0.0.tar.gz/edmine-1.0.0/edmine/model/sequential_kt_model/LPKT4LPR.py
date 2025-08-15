import torch
import torch.nn as nn

from edmine.model.sequential_kt_model.DLSequentialKTModel import DLSequentialKTModel
from edmine.model.module.EmbedLayer import EmbedLayer
from edmine.model.registry import register_model

MODEL_NAME = "LPKT4LPR"


@register_model(MODEL_NAME)
class LPKT4LPR(nn.Module, DLSequentialKTModel):
    model_name = MODEL_NAME

    def __init__(self, params, objects):
        super(LPKT4LPR, self).__init__()
        self.params = params
        self.objects = objects
        
        model_config = self.params["models_config"][MODEL_NAME]
        dim_k = model_config["embed_config"]["question"]["dim_item"]
        dim_correctness = model_config["embed_config"]["correctness"]["dim_item"]
        dim_e = model_config["dim_e"]
        dropout = model_config["dropout"]

        self.embed_layer = EmbedLayer(model_config["embed_config"])
        self.linear_1 = nn.Linear(dim_correctness + dim_e, dim_k)
        self.linear_2 = nn.Linear(3 * dim_k, dim_k)
        self.linear_3 = nn.Linear(3 * dim_k, dim_k)
        self.linear_4 = nn.Linear(2 * dim_k, dim_k)
        self.linear_5 = nn.Linear(dim_e + dim_k, dim_k)

        torch.nn.init.xavier_uniform_(self.linear_1.weight)
        torch.nn.init.xavier_uniform_(self.linear_2.weight)
        torch.nn.init.xavier_uniform_(self.linear_3.weight)
        torch.nn.init.xavier_uniform_(self.linear_4.weight)
        torch.nn.init.xavier_uniform_(self.linear_5.weight)

        self.tanh = nn.Tanh()
        self.sig = nn.Sigmoid()
        self.dropout = nn.Dropout(dropout)
        
        q_matrix = self.objects["dataset"]["q_table_tensor"]
        num_concept = q_matrix.shape[1]
        # self.weight = nn.Parameter(torch.randn(num_concept, dim_k, 1))
        # self.bias = nn.Parameter(torch.randn(num_concept, 1))
        self.latent2ability = nn.Linear(dim_k, 1)
        self.que2difficulty = nn.Linear(dim_e, num_concept)
        self.que2discrimination = nn.Linear(dim_e, 1)

    def forward(self, batch):
        question_seq = batch["question_seq"]
        model_config = self.params["models_config"][MODEL_NAME]
        dim_k = model_config["embed_config"]["question"]["dim_item"]
        q_matrix = self.objects["dataset"]["q_table_tensor"].float()
        num_concept = q_matrix.shape[1]

        batch_size, seq_len = question_seq.size(0), question_seq.size(1)
        e_embed_data = self.embed_layer.get_emb("question", question_seq)
        correctness_data = self.embed_layer.get_emb("correctness", batch["correctness_seq"])

        h_pre = nn.init.xavier_uniform_(torch.zeros(num_concept, dim_k)).repeat(batch_size, 1, 1).to(self.params["device"])
        h_tilde_pre = None
        all_learning = self.linear_1(torch.cat((e_embed_data, correctness_data), 2))
        learning_pre = torch.zeros(batch_size, dim_k).to(self.params["device"])
        pred = torch.zeros(batch_size, seq_len).to(self.params["device"])

        for t in range(0, seq_len - 1):
            e = question_seq[:, t]
            # q_e: (bs, 1, n_skill)
            q_e = q_matrix[e].view(batch_size, 1, -1)

            # Learning Module
            if h_tilde_pre is None:
                h_tilde_pre = q_e.bmm(h_pre).view(batch_size, dim_k)
            learning = all_learning[:, t]

            learning_gain = self.linear_2(torch.cat((learning_pre, learning, h_tilde_pre), 1))
            learning_gain = self.tanh(learning_gain)
            gamma_l = self.linear_3(torch.cat((learning_pre, learning, h_tilde_pre), 1))
            gamma_l = self.sig(gamma_l)
            LG = gamma_l * ((learning_gain + 1) / 2)
            LG_tilde = self.dropout(q_e.transpose(1, 2).bmm(LG.view(batch_size, 1, -1)))

            # Forgetting Module
            # h_pre: (bs, n_skill, d_k)
            # LG: (bs, d_k)
            n_skill = LG_tilde.size(1)
            gamma_f = self.sig(self.linear_4(torch.cat((
                h_pre,
                LG.repeat(1, n_skill).view(batch_size, -1, dim_k)
            ), 2)))
            # bs, num_c, dim_k
            h = LG_tilde + gamma_f * h_pre
            
            # Predicting Module
            next_q2c = q_matrix[question_seq[:, t + 1]]
            # user_ability = torch.sigmoid(torch.einsum('bnd,ndo->bno', h, self.weight) + self.bias).squeeze(dim=-1) * next_q2c
            user_ability = torch.sigmoid(self.latent2ability(h)).squeeze(dim=-1) * next_q2c
            que_difficulty = torch.sigmoid(self.que2difficulty(self.dropout(e_embed_data[:, t + 1]))) * next_q2c
            que_discrimination = torch.sigmoid(self.que2discrimination(self.dropout(e_embed_data[:, t + 1]))) * 5
            y = torch.sigmoid(torch.sum((que_discrimination * (user_ability - que_difficulty)), dim=-1))
            pred[:, t + 1] = y
            
            h_tilde = q_matrix[question_seq[:, t + 1]].view(batch_size, 1, -1).bmm(h).view(batch_size, dim_k)
            # prepare for next prediction
            learning_pre = learning
            h_pre = h
            h_tilde_pre = h_tilde

        return pred

    def get_predict_score(self, batch, seq_start=2):
        mask_seq = torch.ne(batch["mask_seq"], 0)
        predict_score_batch = self.forward(batch)[:, 1:]
        predict_score = torch.masked_select(predict_score_batch[:, seq_start-2:], mask_seq[:, seq_start-1:])

        return {
            "predict_score": predict_score,
            "predict_score_batch": predict_score_batch
        }

    def get_knowledge_state(self, batch, only_last_state=True):
        question_seq = batch["question_seq"]
        model_config = self.params["models_config"][MODEL_NAME]
        dim_k = model_config["embed_config"]["question"]["dim_item"]
        q_matrix = self.objects["dataset"]["q_table_tensor"].float()
        num_concept = q_matrix.shape[1]

        batch_size, seq_len = question_seq.size(0), question_seq.size(1)
        e_embed_data = self.embed_layer.get_emb("question", question_seq)
        correctness_data = self.embed_layer.get_emb("correctness", batch["correctness_seq"])

        h_pre = nn.init.xavier_uniform_(torch.zeros(num_concept, dim_k)).repeat(batch_size, 1, 1).to(self.params["device"])
        h_tilde_pre = None
        all_learning = self.linear_1(torch.cat((e_embed_data, correctness_data), 2))
        learning_pre = torch.zeros(batch_size, dim_k).to(self.params["device"])
        state_history = []

        for t in range(0, seq_len):
            e = question_seq[:, t]
            # q_e: (bs, 1, n_skill)
            q_e = q_matrix[e].view(batch_size, 1, -1)

            # Learning Module
            if h_tilde_pre is None:
                h_tilde_pre = q_e.bmm(h_pre).view(batch_size, dim_k)
            learning = all_learning[:, t]

            learning_gain = self.linear_2(torch.cat((learning_pre, learning, h_tilde_pre), 1))
            learning_gain = self.tanh(learning_gain)
            gamma_l = self.linear_3(torch.cat((learning_pre, learning, h_tilde_pre), 1))
            gamma_l = self.sig(gamma_l)
            LG = gamma_l * ((learning_gain + 1) / 2)
            LG_tilde = self.dropout(q_e.transpose(1, 2).bmm(LG.view(batch_size, 1, -1)))

            # Forgetting Module
            # h_pre: (bs, n_skill, d_k)
            # LG: (bs, d_k)
            n_skill = LG_tilde.size(1)
            gamma_f = self.sig(self.linear_4(torch.cat((
                h_pre,
                LG.repeat(1, n_skill).view(batch_size, -1, dim_k)
            ), 2)))
            # bs, num_c, dim_k
            h = LG_tilde + gamma_f * h_pre
            
            user_ability = torch.sigmoid(self.latent2ability(h)).squeeze(dim=-1)
            state_history.append(user_ability)
            
            if (t + 1) < seq_len:
                h_tilde = q_matrix[question_seq[:, t + 1]].view(batch_size, 1, -1).bmm(h).view(batch_size, dim_k)
                # prepare for next prediction
                learning_pre = learning
                h_pre = h
                h_tilde_pre = h_tilde

        state_history = torch.stack(state_history, dim=1)
        if only_last_state:
            return state_history[torch.arange(batch_size).to(self.params["device"]), batch["seq_len"] - 1]
        else:
            return state_history
    