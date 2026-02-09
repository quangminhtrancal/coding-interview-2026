from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import threading

class Solution:
    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        def get_host_name(url):
            return url.split('/')[2]
        
        host_name = get_host_name(startUrl)
        visited = set()
        visited.add(startUrl)
        visited_lock = threading.Lock()

        def get_link(url):
            new_link = []
            links = htmlParser.getUrls(url)

            for link in links:
                if get_host_name(link) == host_name:
                    with visited_lock:
                        if link not in visited:
                            visited.add(link)
                            new_link.append(link)
            
            return new_link

        with ThreadPoolExecutor(max_workers=10) as executor:
            tasks = {executor.submit(get_link, startUrl)}

            while tasks:
                done, _ = wait(tasks, return_when=FIRST_COMPLETED)

                for future in done:
                    tasks.remove(future)

                    for new_link in future.result():
                        tasks.add(executor.submit(get_link, new_link))
        
        return list(visited)

