def search_tweets(query, resume_token=None, resume_i=0, dry=False):
    params_search = {
    "tweet.fields": "created_at",
    "expansions": "author_id,in_reply_to_user_id,attachments.media_keys,geo.place_id",
    "place.fields": "contained_within,country,country_code,full_name,geo,id,name,place_type",
    "media.fields": "url,public_metrics,type,alt_text",
    "user.fields": "id,verified",
    "max_results": 500,
    "start_time": "2006-12-01T00:00:00Z",
    "end_time": "2022-07-04T00:00:00Z"
    }
    if dry:
        params_search = {
            "start_time": "2006-12-01T00:00:00Z",
            "end_time": "2022-07-04T00:00:00Z",
            "granularity": "day"
        }
        res = s.get(API_ROUTE + COUNT_ROUTE + '?query=' + query, params=params_search)
        print(res.json())
        return res.json()
    new_token = "" if not resume_token else resume_token
    i = resume_i
    total = 0
    while new_token is not None:
        if new_token != "":
            params_search['next_token'] = new_token
        try:
            res = s.get(API_ROUTE + FULL_SEARCH_ROUTE + '?query=' + query, params=params_search)
        except:
            print(resume_token)
        data = res.json()
        count = data.get('meta', {}).get('result_count', 0)
        total += count
        print(f'on a récupéré {total} résultats')
        if  count == 0:
            print(f'aucun résultat pour cette requête')
            print(data)
            new_token = None
        with open(os.path.join(ROOT_FOLDER, str(i) + '.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        new_token = data['meta'].get('next_token', None)
        if i != 0 and i % 10 == 0:
            print("5000 results collected, making a break")
            time.sleep(30)
        i += 1
    print('FINI')