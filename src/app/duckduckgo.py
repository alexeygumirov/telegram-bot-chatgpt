from duckduckgo_search import ddg


MAX_SEARCH_RESULTS = 15
VIDEO_HOSTINGS = ["youtube.com", "vimeo.com", "dailymotion.com", "twitch.tv", "tiktok.co"]


async def web_search(query: str, num_search_results: int = 5):

    try:
        results = ddg(query, region='wt-wt', safesearch='On', time='y', max_results=MAX_SEARCH_RESULTS)
        results_filtered = [result for result in results if not any(video_hosting in result['href'].split("/")[2] for video_hosting in VIDEO_HOSTINGS)]
    except Exception as e:
        print(e)
        return "Something went wrong with Duckduckgo. Try again later.", "ERROR"

    search_result = "Web search results:\n\n"
    for i in range(min(num_search_results, len(results_filtered))):
        # In prompt text list of URLs shall start from 1, not 0
        search_result += f"[{i+1}]: " + results_filtered[i]['body'] + "…" + f"\nURL: {results_filtered[i]['href']}\n"

    return search_result, "OK"
