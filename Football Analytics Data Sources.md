# Understand Football Data Sources

Before going at it alone, it's important to understand what football data exists in the public domain, and equally what doesn't? What do you have to pay for, and what's available for free? 

Through taking the time to consider this, you can appropriately scope your future projects and ensure that the data required to complete them is actually available.

|Data Provider|Data Description|Data Format|
|----------|-------------|:------:|
|[Statsbomb Open Data](https://github.com/statsbomb/open-data)|Statsbomb match event data from a collection of games and competitions|[API](https://github.com/statsbomb/statsbombpy) or [.json](https://github.com/statsbomb/open-data)|
|[Wyscout Free Data](https://figshare.com/collections/Soccer_match_event_dataset/4415000/2)|Wyscout match event data for all matches in Europe's top 5 leagues during 2017-18 season|[.json](https://figshare.com/collections/Soccer_match_event_dataset/4415000/2)|
|[Understat](https://understat.com/)|Shot event data for all matches in Europe's top 5 leages (+ Russian Prem)|[API](https://pypi.org/project/understatapi/) or [Web](https://understat.com/)|
|[FBref](https://fbref.com/en/)|Aggregated team and player data/performance metrics|[Web](https://fbref.com/en/), .xlsx or .csv|
|[Transfermarkt](https://www.transfermarkt.co.uk/)|Team and player market value|[Web](https://www.transfermarkt.co.uk/)|

There are many more data sources, the majority of which are listed and explained within Edd Webster's brilliant [football analytics repository](https://github.com/eddwebster/football_analytics#data-sources). Given the number of web-based resources around, any time spent understanding the basics of web-scraping with Python is time well spent. 


There is a huge amount of research and development that is taking place in the football analytics community, and I'd recommend at least being aware of it. One of the best ways to do this is to take a look at [Jan Van Haaren's](https://www.janvanhaaren.be/) annual soccer analytics review (e.g. [2022 soccer analytics review](https://www.janvanhaaren.be/2022/12/29/soccer-analytics-review-2022.html)). Even if you only scan through the research paper titles, you will at least get an indication of trending research topics and the state-of-the-art in football data analytics.

## Summary

And that's about it! Hopefully this resource has been useful.
