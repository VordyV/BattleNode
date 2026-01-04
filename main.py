from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    from battlenode import BattleNode
    bn = BattleNode()
    bn.run()