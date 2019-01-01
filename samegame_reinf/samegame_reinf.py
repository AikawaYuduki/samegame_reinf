import chainer
import chainer.functions as F
import chainer.links as L
import chainerrl
import numpy as np
import smgm
from random import randint

#盤面をRGBにします！！！！

class QFunction(chainer.Chain):    
    def __init__(self, n_actions):
        super().__init__(
            L0=L.Convolution2D(3 , 16, ksize=8, stride=1),
            L1=L.Convolution2D(16, 32, ksize=4, stride=1),
            L2=L.Convolution2D(32, 32, ksize=3, stride=1),
            L3=L.Linear(1728, 512),
            L4=L.Linear(512, n_actions))
 
    def __call__(self, x, test=False):
        h = F.relu(self.L0(x))
        h = F.relu(self.L1(h))
        h = F.relu(self.L2(h))
        h = F.relu(self.L3(h))
        return chainerrl.action_value.DiscreteActionValue(self.L4(h))
    
def random_action():
    return np.random.randint(0,obs_size,dtype="int")

same = smgm.Game()

# 環境と行動の次元数
obs_size = same.raw * same.line
n_actions = same.raw * same.line
# Q-functionとオプティマイザーのセットアップ
q_func = QFunction(n_actions)
optimizer = chainer.optimizers.Adam(eps=1e-4)
optimizer.setup(q_func)
# 報酬の割引率
gamma = 0.95
# Epsilon-greedyを使ってたまに冒険。50000ステップでend_epsilonとなる
explorer = chainerrl.explorers.LinearDecayEpsilonGreedy(
    start_epsilon=1.0, end_epsilon=0.3, decay_steps=50000, random_action_func=random_action)
# Experience ReplayというDQNで用いる学習手法で使うバッファ
replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity=10 ** 6)
# Agentの生成（replay_buffer等を共有する2つ）
agent = chainerrl.agents.DoubleDQN(
    q_func, optimizer, replay_buffer, gamma, explorer,
    replay_start_size=500, update_interval=1,
    target_update_interval=100)

#学習ゲーム回数
n_episodes = 20000
n_turn = 100

for i in range(1, n_episodes + 1):
    same.make_board()
    reward = 0
    turns = 0
    while turns < n_turn:
        #配置マス取得
        b = same.torgb()
        action = agent.act_and_train(b, reward)
        #配置を実行
        same.click(action)
        #配置の結果、終了時には報酬とカウンタに値をセットして学習
        if same.is_clear() == True:
            reward = 1000
            break
        else:
            turns += 1

    reward += same.score()
    #エピソードを終了して学習
    agent.stop_episode_and_train(b, reward, True)

    #コンソールに進捗表示
    if i % 1 == 0:
        print("episode:", i, " / reward:", reward ," / statistics:", agent.get_statistics(), " / epsilon:", agent.explorer.epsilon)
    if i % 1000 == 0:
        # 10000エピソードごとにモデルを保存
        agent_p1.save("result_" + str(i))


print("Training finished.")