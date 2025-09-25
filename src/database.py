import peewee


database = peewee.SqliteDatabase("lotr_lcg.db")


class CardSide(peewee.Model):
    Slug = peewee.CharField(primary_key=True)
    Title = peewee.CharField()
    Sphere = peewee.CharField(null=True)
    Type = peewee.CharField()
    Subtype = peewee.CharField(null=True)
    Text = peewee.CharField()
    FlavorText = peewee.CharField(null=True)
    Traits = peewee.CharField()
    Keywords = peewee.CharField()

    Attack = peewee.IntegerField(null=True)
    Defense = peewee.IntegerField(null=True)
    HitPoints = peewee.IntegerField(null=True)
    IsUnique = peewee.BooleanField(null=True)
    ThreatCost = peewee.IntegerField(null=True)
    Willpower = peewee.IntegerField(null=True)
    ResourceCost = peewee.IntegerField(null=True)
    VictoryPoints = peewee.IntegerField(null=True)
    QuestPoints = peewee.IntegerField(null=True)
    ThreatStrength = peewee.IntegerField(null=True)
    EngagementCost = peewee.IntegerField(null=True)
    ShadowEffect = peewee.CharField(null=True)
    MaxPerDeck = peewee.IntegerField(null=True)
    Orientation = peewee.CharField()
    Direction = peewee.CharField(null=True)
    Stage = peewee.CharField(null=True)

    Search_Title = peewee.CharField()

    class Meta:
        database = database
        table_name = "cardSides"


class Card(peewee.Model):
    Slug = peewee.CharField(primary_key=True)
    Front = peewee.ForeignKeyField(CardSide, db_column="FrontSlug")
    Back = peewee.ForeignKeyField(CardSide, db_column="BackSlug", null=True)
    IsRCO = peewee.BooleanField()

    class Meta:
        database = database
        table_name = "cards"


class Product(peewee.Model):
    Code = peewee.CharField(primary_key=True)
    Name = peewee.CharField()
    Type = peewee.CharField()
    Cycle = peewee.CharField(null=True)
    IsRepackage = peewee.BooleanField()

    class Meta:
        database = database
        table_name = "products"


class ProductCard(peewee.Model):
    Product = peewee.ForeignKeyField(Product, db_column="ProductCode")
    Number = peewee.CharField()
    Card = peewee.ForeignKeyField(Card, db_column="CardSlug", backref="ProductCards")
    Quantity = peewee.IntegerField()
    FrontImageUrl = peewee.CharField()
    BackImageUrl = peewee.CharField(null=True)
    BackNumber = peewee.CharField(null=True)

    class Meta:
        database = database
        table_name = "productCards"
        primary_key = False


class Glossary(peewee.Model):
    Term = peewee.CharField(primary_key=True)
    Type = peewee.CharField()
    Definition = peewee.CharField()

    class Meta:
        database = database
        table_name = "glossary"


database.connect()
