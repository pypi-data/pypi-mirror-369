import subprocess


def say(text):
    out = ""

    if "CAT!!!" in text:
        out += (subprocess.run(
            text.replace("CAT!!!", ""),  # сама команда (в виде списка)
            capture_output=True,  # захватываем вывод
            text=True,  # получаем не байты, а строку
            shell=True
        )).stdout

    out += text.upper()
    out += ("""
    \\\\
      \\\\
        \\\\
        
    | | | | | | |   | |  | | | | | |
    | \\|/  \\|/  |   ||  | | | | | |
    |  |    |   |   ||  | | | | | |
    """)
    return out


if __name__ == '__main__':
    print(say("CAT!!!dir"))
