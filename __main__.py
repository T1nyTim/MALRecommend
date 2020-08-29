from argparse import Namespace, ArgumentParser
from time import sleep

import api
from __init__ import TOP_DIR


def get_arguments() -> Namespace:
    parser = ArgumentParser()
    # TODO: validate args
    parser.add_argument('--username', type=str, default=None)
    parser.add_argument('--score', type=int, default=7) # range 1 to 10
    parser.add_argument('--nsfw', type=bool, default=True)
    return parser.parse_args()

def main():
    if not api.user_authorization():
        return
    watched_list = api.get_watched_list(args.username)
    recommend = {}
    print(f"Max time to pull details of your completed list is {len(watched_list) / 2}s")
    for id in watched_list.keys():
        anime = api.get_anime(id)
        if not anime:
            print(f"Anime with ID {id} was not found")
            continue
        if anime['rating'] < args.score:
            break
        if not args.nsfw:
            continue
        for rec in anime['recommendations']:
            if rec['id'] in watched_list:
                continue
            else:
                your_weight = rec['rec_num'] * anime['rating']
                user_weight = int(rec['rec_num'] * anime['score'])
                if rec['id'] in recommend:
                    recommend[rec['id']]['recs'] += 1
                    recommend[rec['id']]['rec_num'] += rec['rec_num']
                    recommend[rec['id']]['your_weight'] += your_weight
                    recommend[rec['id']]['user_weight'] += user_weight
                else:
                    recommend[rec['id']] = {
                        'title': rec['title'],
                        'recs': 1,
                        'rec_num': rec['rec_num'],
                        'your_weight': your_weight,
                        'user_weight': user_weight
                    }
                #print(f"Title: {rec['title']} | Recs: {rec['rec_num']} | Score: {your_weight} | UserScore: {user_weight}")
        sleep(0.5)
    print("Creating csv of results")
    with open(TOP_DIR.joinpath(f"{args.username or 'Tim'}.csv"), 'w', encoding='UTF-8') as csv_file:
        csv_file.write('title,rec_num,your_weight,user_weight\n')
        for rec in recommend.values():
            csv_file.write(f"{rec['title'].replace(',','')},{rec['rec_num']},{rec['your_weight']},{rec['user_weight']}\n")


args = get_arguments()
if __name__ == '__main__':
    main()