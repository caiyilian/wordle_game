from game import Wordle, random_word, GuessResult

def main():
    dic_name = "CET4"
    word_length = 5
    
    word, meaning = random_word(dic_name, word_length)
    # print(word) # Debug: uncomment to see the answer
    game = Wordle(word, meaning)

    print(f"猜单词游戏开始！单词长度为{word_length}，你有{game.rows}次机会猜出单词。")

    while True:
        try:
            guess = input("请输入你的猜测：").strip()
        except KeyboardInterrupt:
            print("\n游戏结束。")
            break

        if not guess:
            continue

        if guess == "提示":
            hint = game.get_hint()
            print(f"提示：{hint}")
            with open("current_guess_hint.png", "wb") as f:
                f.write(game.draw_hint(hint).getbuffer())
            print("提示图像已保存为 current_guess_hint.png")
            continue

        result = game.guess(guess)

        if result == GuessResult.WIN:
            print(f"恭喜你猜出了单词！\n{game.result}")
            img_data = game.draw()
            with open("current_guess.png", "wb") as f:
                f.write(img_data.getbuffer())
            print("最终结果已保存为 current_guess.png")
            break
        elif result == GuessResult.LOSS:
            print(f"很遗憾，你没有猜出单词。\n{game.result}")
            break
        elif result == GuessResult.DUPLICATE:
            print("你已经猜过这个单词了。")
        elif result == GuessResult.ILLEGAL:
            print("你输入的不是一个合法的单词。")
        else:
            print("继续猜测吧！")

        # 显示当前猜测结果的图像
        img_data = game.draw()
        with open("current_guess.png", "wb") as f:
            f.write(img_data.getbuffer())
        print("当前猜测结果已保存为 current_guess.png")

if __name__ == "__main__":
    main()
