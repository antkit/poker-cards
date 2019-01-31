import json
import tkinter as tk
import tkinter.messagebox
from PIL import ImageTk, Image


class Application(tk.Frame):
    """
    扑克游戏辅助工具，便于调试，用于可视化发牌和查看打出的牌。
    输入和输出JSON中，扑克牌值从小到大的花色依次为方块、梅花、红心、黑桃和王。
    每个花色从该花色的3开始到2结束（345678910JQKA2）。方块3对应牌值0，依序递增，比如[0, 1, 11, 12, 13]代表方块3、4、A、2和梅花3。
    对于大小王，52对应小王，53对应大王。
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.card_label = None
        self.card_text = None
        self.btn_reset = None
        self.btn_confirm = None
        self.card_buttons = []
        self.card_photos = []
        self.card_characters = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k']  # 牌值
        self.card_serials = ['d', 'c', 'h', 's', 'j']  # 花色，依次为方块、梅花、红心、黑桃和王
        self.selected_cards = []
        self.card_board = None
        self.card_board_buttons = []
        self.card_board_photos = []
        self.master = master
        self.pack()
        self.create_widgets()

    def button_callback(self, row, column):
        return lambda: self.card_selected(row, column + 1)

    def create_card_button(self, row, column):
        btn = tk.Button(self)
        btn['text'] = '%d.%d' % (row, column)
        btn['command'] = self.button_callback(row, column)
        path = self.card_image_path(row, column + 1)
        image = Image.open(path)
        image = image.resize((int(image.width * 0.7), int(image.height * 0.7)), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image=image)
        btn.config(image=photo)
        btn.grid(row=row, column=column)
        self.card_photos.append(photo)
        self.card_buttons.append(btn)

    def create_widgets(self):
        for r in range(0, 4):
            for c in range(0, 13):
                self.create_card_button(r, c)
        self.create_card_button(4, 0)
        self.create_card_button(4, 1)

        self.card_label = tk.Label(self, text=' 扑 克：')
        self.card_label.grid(row=5, column=0)

        self.card_text = tk.Text(self, height=2)
        self.card_text.grid(row=5, column=1, columnspan=8)

        self.btn_confirm = tk.Button(self, text=' 确 认 ', command=self.confirm_cards)
        self.btn_confirm.grid(row=5, column=9)

        self.btn_reset = tk.Button(self, text=' 重 置 ', command=self.reset_cards)
        self.btn_reset.grid(row=5, column=10)

        self.card_board = tk.Frame(self)
        self.card_board.grid(row=6, column=0, columnspan=13)

    def card_image_path(self, serial, value):
        """
        扑克牌对应的图像文件路径。
        :param serial: 花色索引
        :param value: 牌值，1对应A，2对应2，11对应J
        :return: 该扑克牌对应的图像文件路径
        """
        if serial < 4:
            return 'res/%s%s.jpg' % (self.card_characters[value - 1], self.card_serials[serial])
        return 'res/%s_joker.jpg' % ('black' if value - 1 == 0 else 'red')

    def card_selected(self, serial, value, refresh=True):
        path = self.card_image_path(serial, value)
        image = Image.open(path)
        image = image.resize((int(image.width * 0.4), int(image.height * 0.4)), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image=image)
        btn = tk.Button(self.card_board)
        btn.config(image=photo)
        btn.grid(row=int(len(self.card_board_buttons) / 18), column=int(len(self.card_board_buttons) % 18))
        self.card_board_photos.append(photo)
        self.card_board_buttons.append(btn)
        self.card_label['text'] = ' 扑 克 - %d:' % len(self.card_board_buttons)

        self.selected_cards.append({'s': serial, 'v': value})
        if refresh:
            self.refresh()

    def reset_cards(self):
        self.reset_selected()
        self.card_text.delete('1.0', tk.END)
        self.card_label['text'] = ' 扑 克:'

    def confirm_cards(self):
        self.reset_selected()
        text = self.card_text.get('1.0', tk.END)
        if len(text) < 2:
            return

        try:
            js = json.loads(text)
        except json.decoder.JSONDecodeError as e:
            tk.messagebox.showwarning('Error', e.msg)
            return
        for cv in js:
            serial = int(cv / 13)
            if cv == 52 or cv == 53:
                value = 1 if cv == 52 else 2
            else:
                value = (cv % 13) + 3
                if value > 13:
                    value -= 13
            self.card_selected(serial, value, refresh=False)

    def reset_selected(self):
        for btn in self.card_board_buttons:
            btn.destroy()
        self.card_board_buttons.clear()
        self.selected_cards.clear()
        self.card_board_photos.clear()

    def refresh(self):
        data = []
        for card in self.selected_cards:
            if card['s'] == 4:
                data.append(card['s'] * 13 + card['v'] - 1)
            elif card['v'] < 3:
                data.append(card['s'] * 13 + 11 + card['v'] - 1)
            else:
                data.append(card['s'] * 13 - 2 + card['v'] - 1)
        self.card_text.delete('1.0', tk.END)
        self.card_text.insert(tk.INSERT, json.dumps(data))


root = tk.Tk()
root.title('Poker')
app = Application(master=root)
app.mainloop()
