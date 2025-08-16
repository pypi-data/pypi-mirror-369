from npycli import CLI

cli = CLI()


@cli.cmd(name='sum')
def sum_cmd(*args: int) -> None:
    print(sum(args))


if __name__ == '__main__':
    while True:
        cli.prompt()
