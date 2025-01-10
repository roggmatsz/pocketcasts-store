class ListenRecord:
    def __init__(self, episode_uuid, url, published_date, duration,
                 title, size, is_starred, podcast_uuid, podcast_title,
                 author, date_added, id = None
                ):
        self.id = id
        self.episode_uuid = episode_uuid
        self.url = url
        self.published_date = published_date
        self.duration = duration
        self.title = title
        self.size = size
        self.is_starred = is_starred
        self.podcast_uuid = podcast_uuid
        self.podcast_title = podcast_title
        self.author = author
        self.date_added = date_added

    @classmethod
    def Convert_List(cls, source_list):
        packaged_list = []

        for row in source_list:
            packaged_list.append(ListenRecord.From_Row_List(row))
        
        return packaged_list

    @classmethod
    def From_Dictionary(cls, source_dictionary):
        id, episode_uuid, url, published_date, duration, title, size, is_starred, podcast_uuid, podcast_title, author, date_added = source_dictionary.values()

        return cls(episode_uuid, url, published_date, duration, title, size, is_starred, podcast_uuid, podcast_title, author, date_added, id)

    @classmethod
    def From_Row_List(cls, source_list):
        id, episode_uuid, url, published_date, duration, title, size, is_starred, podcast_uuid, podcast_title, author, date_added = source_list
        
        return cls(episode_uuid, url, published_date, duration, title, size, is_starred, podcast_uuid, podcast_title, author, date_added, id)
    
    def __eq__(self, other):
        if isinstance(other, ListenRecord):
            return (self.episode_uuid == other.episode_uuid and
                    self.url == other.url and
                    self.published_date == other.published_date and
                    self.duration == other.duration and
                    self.title == other.title and
                    self.size == other.size and 
                    self.is_starred == other.is_starred and
                    self.podcast_uuid == other.podcast_uuid and
                    self.podcast_title == other.podcast_title and
                    self.author == other.author)
        
        return False
    
    def __repr__(self):
        return 'ListenRecord\n - ID: {}\n - Episode UUID: {}\n - URL: {}\n - Published Date: {}\n - Duration: {}\n - Title: {}\n - Size: {}\n - Is Starred: {}\n - Podcast UUID: {}\n - Podcast Title: {}\n - Author: {}\n - Date Added: {}'.format(
            self.id, self.episode_uuid, self.url, self.published_date, self.duration, self.title, self.size, self.is_starred, self.podcast_uuid, self.podcast_title, self.author, self.date_added
        )