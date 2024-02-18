from django.contrib import admin
from django.contrib import admin

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from scrapper.models import *


class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        use_transactions = True
        # exclude = ('id',)
        # import_id_fields = ('skuid', 'category')
        # import_id_fields = ('skuid', 'category', 'retailer_client')

    def before_import_row(self, row, **kwargs):
        if row.keys():
            for col in row.keys():
                if "author" in col.lower():
                    author = row.get(col)
                    if author:
                        author = author.lower().strip()
                        author_ins = Author.objects.get_or_create(name=author)[0]
                        # author_ins = Author.objects.filter(name=author)
                        # if author_ins.exists():
                        #     author_ins = Author.objects.get(name=author)
                        # else:
                        #     ins = Author(name=author).save()
                        #     # Author.objects.create(name=author)
                        #     author_ins = Author.objects.filter(name=author)[0]

                        row['author'] = author_ins.id
                        break

            for col in row.keys():
                if "publication" in col.lower():
                    publication = row.get(col)
                    if publication:
                        publication = publication.lower().strip()
                        publication_ins = Publication.objects.get_or_create(name=publication)[0]
                        # publication_ins = Publication.objects.filter(name=publication)
                        # if publication_ins.exists():
                        #     publication_ins = Publication.objects.get(name=publication)
                        # else:
                        #     ins = Publication(name=publication).save()
                        #     # Publication.objects.create(name=publication)
                        #     publication_ins = Publication.objects.filter(name=publication)[0]

                        row['publication'] = publication_ins.id
                        break

            for col in row.keys():
                if "date_publish" in col.lower():
                    date = row.get(col)
                    row['date_publish'] = date.strip()
                    break

    def skip_row(self, instance, original):
        # print(str(instance.date))
        # print(original.date)
        if not str(instance.date)[0].isdigit():
            return True


@admin.register(Article)
class ArticleResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'author_display', 'publication', 'title', 'source_url', 'keywords_display', 'tags_display',
                    'date_publish']
    search_fields = ['author', 'publication', 'title']
    list_filter = ['author', 'publication', 'keywords', 'state', 'is_tweet']
    resource_class = ArticleResource

    def author_display(self, obj):
        return ", ".join([author.name for author in obj.author.all()])

    def publication(self, obj):
        try:
            return obj.publication.name
        except:
            return None

    def keywords_display(self, obj):
        return ", ".join([keyword.name for keyword in obj.keywords.all()])

    def tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    keywords_display.short_description = "Keywords"
    tags_display.short_description = "Tags"


class AuthorResource(resources.ModelResource):
    class Meta:
        model = Author
        use_transactions = True


@admin.register(Author)
class AuthorResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = AuthorResource


class PublicationResource(resources.ModelResource):
    class Meta:
        model = Publication
        use_transactions = True


@admin.register(Publication)
class PublicationResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = PublicationResource


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        use_transactions = True


@admin.register(Category)
class CategoryResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = CategoryResource


class KeywordResource(resources.ModelResource):
    class Meta:
        model = Keyword
        use_transactions = True


@admin.register(Keyword)
class KeywordResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'is_enable', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = KeywordResource


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        use_transactions = True


@admin.register(Location)
class LocationResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = LocationResource


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag
        use_transactions = True


@admin.register(Tag)
class TagResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = TagResource


class TargetURLResource(resources.ModelResource):
    class Meta:
        model = TargetURL
        # fields = ('url', 'selector', 'state', 'city')
        use_transactions = True

    def before_import_row(self, row, **kwargs):

        # Access the TargetURL object from the database using the 'url' field

        # Create or retrieve State objects and add them to the TargetURL instance
        if row['state']:
            state, created = State.objects.get_or_create(name=row['state'])
            row['state'] = state.id
        #
        # # Create or retrieve City objects and add them to the TargetURL instance
        if row['city']:
            city, created = City.objects.get_or_create(name=row['city'])
            row['city'] = city.id


@admin.register(TargetURL)
class TargetURLResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'url', 'selector', 'is_active', 'created_on', 'updated_on']
    search_fields = ['url', ]
    resource_class = TargetURLResource


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        use_transactions = True


@admin.register(Country)
class CountryResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = CountryResource


class StateResource(resources.ModelResource):
    class Meta:
        model = State
        use_transactions = True


@admin.register(State)
class StateResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = StateResource


class CityResource(resources.ModelResource):
    class Meta:
        model = City
        use_transactions = True


@admin.register(City)
class CityResourceResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = CityResource


class PeopleResource(resources.ModelResource):
    class Meta:
        model = People
        use_transactions = True


@admin.register(People)
class PeopleResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = PeopleResource


class KeywordSentimentResource(resources.ModelResource):
    class Meta:
        model = KeywordSentiment
        use_transactions = True


@admin.register(KeywordSentiment)
class KeywordSentimentResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'article', 'keyword', 'sentiment_score']
    search_fields = ['article', ]
    resource_class = KeywordSentimentResource


class PeopleSentimentResource(resources.ModelResource):
    class Meta:
        model = PeopleSentiment
        use_transactions = True


@admin.register(PeopleSentiment)
class PeopleSentimentResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'article', 'people', 'sentiment_score']
    search_fields = ['article', ]
    resource_class = PeopleSentimentResource


class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project
        use_transactions = True


@admin.register(Project)
class ProjectResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = ProjectResource
