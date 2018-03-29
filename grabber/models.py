from django.db import models


class Site(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.title

    class Meta:
        ordering = ('id',)


class Auction(models.Model):
    number = models.PositiveIntegerField()
    date = models.DateField(null=True)
    url = models.URLField(null=True)
    site = models.ForeignKey('Site', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s #%d" % (self.site.title, self.number)

    class Meta:
        unique_together = ('site', 'number')
        ordering = ('number',)


class Category(models.Model):
    title = models.CharField(max_length=100)
    site = models.ForeignKey('Site', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('site', 'title')
        ordering = ('id',)


class Completion(models.Model):
    STATUS = (
        ('n', 'New'),
        ('p', 'In process'),
        ('d', 'Done'),
    )
    status = models.CharField(max_length=1, choices=STATUS, default='n')
    total = models.PositiveSmallIntegerField(null=True)
    processed = models.PositiveSmallIntegerField(null=True)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.processed is None or self.total is None:
            return "%s | %s New" % (self.auction, self.category)
        else:
            return "%s | %s <%d/%d>" % (self.auction, self.category,
                                        self.processed, self.total)

    class Meta:
        unique_together = ('auction', 'category')
        ordering = ('-updated_at',)


class Raw(models.Model):
    url = models.URLField(unique=True)
    html = models.TextField()
    auction = models.ForeignKey('Auction', on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
