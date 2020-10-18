import datetime
from haystack import indexes
from article.models import Article

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    # text = indexes.EdgeNgramField(document=True, use_template=True, template_name="../../article/templates/search/indexes/article/article_text.txt")
    abstract = indexes.CharField(model_attr='abstract', null=True)
    # submitter = indexes.CharField(model_attr='submitter', null=True)
    # authors = indexes.CharField(model_attr='authors', null=True)
    title = indexes.CharField(model_attr='title', null=True)
    # categories = indexes.CharField(model_attr='categories', null=True)
    # update_date = indexes.CharField(model_attr='update_date', null=True)

    def get_model(self):
        print('getting model', Article.abstract)
        return Article

    def index_queryset(self, using=None):
        print('processing..')
        print(self.get_model().objects.all())
        return self.get_model().objects.all()
