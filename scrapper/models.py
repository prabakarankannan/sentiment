from django.db import models
from django.conf import settings
from urllib.parse import urlparse

# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=160, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Authors"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Author, self).save(*args, **kwargs)


class Publication(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Publications"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Publication, self).save(*args, **kwargs)


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Locations"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Location, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Category, self).save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Tags"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Tag, self).save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Countries"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Country, self).save(*args, **kwargs)


class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "States"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(State, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Cities"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(City, self).save(*args, **kwargs)


class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_enable = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Keywords"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(Keyword, self).save(*args, **kwargs)


class People(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "People"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = str(self.name).lower()
        return super(People, self).save(*args, **kwargs)


class Article(models.Model):
    author = models.ManyToManyField(Author)
    publication = models.ForeignKey(Publication, on_delete=models.SET_NULL, null=True)
    category = models.ManyToManyField(Category)

    location = models.ManyToManyField(Location)
    country = models.ManyToManyField(Country)
    state = models.ManyToManyField(State)
    city = models.ManyToManyField(City)

    # Many-to-Many relationships with Keyword and Person
    keywords = models.ManyToManyField(Keyword)
    people = models.ManyToManyField(People)

    tags = models.ManyToManyField(Tag)

    title = models.TextField(null=True)
    content = models.TextField(null=True)

    source_title = models.TextField(null=True)
    source_content = models.TextField(null=True)
    source_language = models.CharField(max_length=15, null=True)

    source_url = models.URLField(null=True, unique=True)
    image_url = models.URLField(null=True)

    sentiment_compound = models.FloatField(null=True)

    date_publish = models.DateTimeField(null=True)

    is_tweet = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        if len(str(self.source_content))>20:
            return str(self.source_content[:20])
        else:
            return str(self.source_content)

    class Meta:
        verbose_name_plural = "Articles"
        # unique_together = ('author', 'publication','title')


class KeywordSentiment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    sentiment_score = models.FloatField()

    def __str__(self):
        return str(self.article.name) + " --> " + str(self.keyword.name)

    class Meta:
        verbose_name_plural = "Keyword Sentiments"
        unique_together = ('article', 'keyword')


class PeopleSentiment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    sentiment_score = models.FloatField()

    def __str__(self):
        return str(self.article.name) + " --> " + str(self.people.name)

    class Meta:
        verbose_name_plural = "People Sentiments"
        unique_together = ('article', 'people')


class TargetURL(models.Model):
    url = models.URLField()
    domain = models.CharField(max_length=255, blank=True)  # New field for the domain

    state = models.ManyToManyField(State)  # New field for the domain
    city = models.ManyToManyField(City)  # New field for the domain

    selector = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.url)

    def save(self, *args, **kwargs):
        parsed_url = urlparse(str(self.url))
        if parsed_url.netloc:
            domain = parsed_url.netloc
            if domain.startswith("www."):
                self.domain = domain[4:]
            else:
                self.domain = domain

        super(TargetURL, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "TargetURL"
        unique_together = ('url', 'selector')


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)  # New field for the domain

    keyword = models.ManyToManyField(Keyword)
    state = models.ManyToManyField(State)  # New field for the domain

    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)







