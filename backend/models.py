from django.db import models

# Create your models here.


class CrawlWebsite(models.Model):
    url = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    lock = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    lastest_time = models.TextField(null=True)

    def __unicode__(self):
        return self.url

    def __str__(self):
        return self.url

    class Meta:
        db_table = "crawl_website"


class Customer(models.Model):
    name = models.CharField(max_length=45)
    user_level = models.CharField(max_length=45)
    total_comment = models.IntegerField(blank=False, null=True)
    useful_num = models.IntegerField(blank=False, null=True)
    upload_img_num = models.IntegerField(blank=False, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = "customer"


class Hotel(models.Model):
    name = models.CharField(max_length=45)
    addr = models.CharField(max_length=45, null=True)
    desc = models.TextField(blank=True, null=True)
    policy = models.TextField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    traffic = models.TextField(blank=True, null=True)
    score = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    # phone = models.CharField(max_length=45, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = "hotel"


class RoomType(models.Model):
    name = models.CharField(max_length=45) # the room's type name
    hotel = models.ForeignKey(Hotel)
    desc = models.CharField(max_length=255, null=True)
    price = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = "room_type"


class Comment(models.Model):
    customer = models.ForeignKey(Customer)
    hotel = models.ForeignKey(Hotel)
    room_type = models.ForeignKey(RoomType)
    score_position = models.FloatField(blank=True, null=True)
    score_equipment = models.FloatField(blank=True, null=True)
    score_service = models.FloatField(blank=True, null=True)
    score_health = models.FloatField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    datetime = models.CharField(max_length=45, null=True)
    useful_num = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.customer.name + '@' + self.hotel.name

    def __str__(self):
        return self.customer.name + '@' + self.hotel.name

    class Meta:
        db_table = "comment"
