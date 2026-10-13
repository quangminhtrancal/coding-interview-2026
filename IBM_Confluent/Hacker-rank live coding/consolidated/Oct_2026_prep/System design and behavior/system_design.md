https://leetcode.com/discuss/post/7687348/confluent-sse-system-design-round-what-t-z2nd/
Was asked temp email generator HLD , API , Entities , DB Choices, NFR


https://leetcode.com/discuss/post/8545763/confluent-uk-remote-interview-experience-68jv/
System Design
Building a podcast service, focus on feed generation.



https://leetcode.com/discuss/post/5634790/confluent-sse-bengaluru-remote-by-anonym-rop3/ 
questions around scaling

how to detect bottlenecks in system and how to remedy them

talked about load balancers, access logs of LB, multi region LB and regional routing
talked about slow query detection and remedies, db load analysis and master slave archi with replica lag b/w master slave
talked about IAC like terraform to maintain infra and deploy multi-region
talked about splitting monolith to microservices and how to go about it
each question focuses on hld first then followed by how to actually do it in cloud


https://leetcode.com/discuss/post/4188001/confluent-seniorstaff-software-engineer-5219u/
Design round: TinyUrl (Constraints: optimize only for high volume of reads - a simple singleton service with a sharded database(range based sharding on short url would suffice. You can add more read replicas with additional caching at the edge if needed). Do not make it complex

Design round 1(API design) - Spotify like system. Design APIs to retrieve X podcast channels at a time, X audio clips per podcast channel, Database design and high level component design [pagination, skip tokens, limit/offset, api versioning, back of the napkin calculation for number of users to number of podcast channels, podcast channel to number of audio clips per channel, corner cases[users subscribed to a lot of channels, channels with a lot of videos, etc.,]]



