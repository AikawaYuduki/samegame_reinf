import random
import numpy as np

#盤の縦横サイズ
RAW = 15
LINE = 30

#ゲームのクラス
class Game:
    def __init__(self,raw=RAW,line=LINE):
        self.raw = raw
        self.line = line
        self.n_mass = self.raw*self.line
        self.make_board()

    #盤面を作る
    def make_board(self):
        self.board = [0 for i in range(self.n_mass)]

        #色は1,2,3,4 0は空白
        for i in range(self.n_mass):
            self.board[i] = (i%4) + 1
        random.shuffle(self.board)

        return self.board

    #上下左右に盤面があるかの判定
    def exist_board(self,pos):
        self.ex_bor = {"right":True,"up":True,"left":True,"down":True}
        #上
        if pos < self.raw:
            self.ex_bor["up"] = False
        #左
        if pos%self.line == 0:
            self.ex_bor["left"] = False
        #右
        if (pos+1)%self.line == 0:
            self.ex_bor["right"] = False
        #下
        if (pos // self.line) == (self.raw - 1):
            self.ex_bor["down"] = False

        return self.ex_bor

    #隣が同じ色か
    def samecolor_a(self,pos):
        if self.board[pos] != 0:
            #右
            if self.exist_board(pos)["right"]:
                if not self.checked[pos+1]:
                    if self.board[pos] == self.board[pos+1]:
                        self.checked[pos+1] = True
                        self.sames.append(pos+1)
                        self.samecolor_a(pos+1)

            #上
            if self.exist_board(pos)["up"]:
                if not self.checked[pos-self.line]:
                    if self.board[pos] == self.board[pos-self.line]:
                        self.checked[pos-self.line] = True
                        self.sames.append(pos-self.line)
                        self.samecolor_a(pos-self.line)

            #左
            if self.exist_board(pos)["left"]:
                if not self.checked[pos-1]:
                    if self.board[pos] == self.board[pos-1]:
                        self.checked[pos-1] = True
                        self.sames.append(pos-1)
                        self.samecolor_a(pos-1)

            #下
            if self.exist_board(pos)["down"]:
                if not self.checked[pos+self.line]:
                    if self.board[pos] == self.board[pos+self.line]:
                        self.checked[pos+self.line] = True
                        self.sames.append(pos+self.line)
                        self.samecolor_a(pos+self.line)


    def samecolor(self,pos):
        #チェック済みかのリストを初期化
        self.checked = [False for i in range(self.n_mass)]
        #同じ色リストを初期化
        self.sames = [pos]

        self.samecolor_a(pos)

        return self.sames

    #同じやつを消す
    def delete(self,pos):
        self.samestemp = self.samecolor(pos)
        if not len(self.samestemp) == 1:
            for i in self.samestemp:
                self.board[i] = 0

    #横を詰める
    def yoko_tsume(self):
        tsumetakana = False
        #空じゃない列
        empline = list(range(self.line))
        for i in range(self.line):
            #縦のリストを作ります
            self.tate_pos = [(j*self.line)+i for j in range(self.raw)]
            self.tate = [self.board[j] for j in self.tate_pos]
            #詰める
            #すべてが0かという判定
            if all([x==0 for x in self.tate]):
                #空の列は除きましょうね
                empline.remove(i)
                tsumetakana = True
                
        #空じゃない列を左から詰めて再描写
        if tsumetakana:
            for i in range(self.line):
                if i+1 <= len(empline):
                    for j in range(self.raw):
                        self.board[(self.line*j)+i] = self.board[(self.line*j)+empline[i]]
                else:
                    for j in range(self.raw):
                        self.board[(self.line*j)+1] = 0

                 
    def tate_tsume(self):
        for i in range(self.line):
            tsumetakana = False
            #縦のリストを作ります
            self.tate_pos = [(j*self.line)+i for j in range(self.raw)]
            self.tate = [self.board[j] for j in self.tate_pos]
            #空のますを抜いてしたからつめて再描写。
            self.tate = [j for j in self.tate if not j == 0]
            for j in range(self.raw):
                if j+1 <= len(self.tate):
                    self.board[((self.raw-j-1)*self.line)+1] = self.tate[-(j+1)]
                else:
                    self.board[((self.raw-j-1)*self.line)+1] = 0

    #クリアしたかな？
    def is_clear(self):
        self.done = True
        for i in range(self.n_mass):
            if self.exist_board(i)["right"]:
                self.done = False
                break
            if self.exist_board(i)["up"]:
                self.done = False
                break
            if self.exist_board(i)["left"]:
                self.done = False
                break
            if self.exist_board(i)["down"]:
                self.done = False
                break
            
        return self.done

    def click(self,pos):
        #self.samecolor(pos)
        self.delete(pos)
        self.yoko_tsume()
        self.tate_tsume()

        return self.board

    def score(self):
        self.scores = 0
        for i in self.board:
            if i == 0:
                self.scores += 1

        return self.scores

    def torgb(self):
        colors = {0:[0,0,0],1:[1,0,0],2:[0,1,0],3:[0,0,1],4:[1,1,1]}
        rgbboard = [0 for i in range(self.n_mass*3)]
        for i in range(self.n_mass):
            rgbboard[i] = colors[self.board[i]][0]
            rgbboard[i+(self.n_mass)] = colors[self.board[i]][1]
            rgbboard[i+(self.n_mass*2)] = colors[self.board[i]][2]

        rgbboard = np.array(rgbboard,dtype="float32")
        rgbboard = rgbboard.reshape([3,self.raw,self.line])

        return rgbboard

    def toimg(self):
        colors = {0:[0,0,0],1:[255,0,0],2:[0,255,0],3:[0,0,255],4:[255,255,255]}
        image = [0 for i in range(self.n_mass)]
        for i in range(self.n_mass):
            image[i] = colors[self.board[i]]

        image = np.array(image,dtype="uint8")
        image = image.reshape([self.raw,self.line,3])
        return image