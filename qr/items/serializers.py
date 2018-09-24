from rest_framework import serializers

from items.models import Brand, CheckIn, Item, LostItem, TypeItem


class ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=200)
    reference = serializers.CharField(max_length=30)
    color = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=255)
    lost = serializers.BooleanField(default=False)
    type_item = serializers.CharField(max_length=30)
    brand = serializers.CharField(max_length=30)
    registered_in_seat_id = serializers.IntegerField()
    company_id = serializers.IntegerField()
    registered_in_seat = serializers.CharField(max_length=100)
    registration_date = serializers.DateTimeField()
    registered_by = serializers.IntegerField()
    owner_name = serializers.CharField(max_length=50)
    owner_last_name = serializers.CharField(max_length=50)
    owner_dni = serializers.CharField(max_length=30)


class ItemUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('reference',
                  'color',
                  'lost',
                  'lost_date',
                  'type_item',
                  'brand')
        read_only_fields = (
            'registered_by', 'seat_registration', 'registration_date', 'lost_date')


class ChekinSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    seat_id = serializers.IntegerField()
    seat_dir = serializers.CharField(max_length=30)
    seat_name = serializers.CharField(max_length=255)
    item_id = serializers.IntegerField()
    type_item = serializers.CharField(max_length=255)
    lost = serializers.BooleanField(default=False)
    owner_name = serializers.CharField(max_length=50)
    owner_last_name = serializers.CharField(max_length=50)
    owner_dni = serializers.CharField(max_length=30)
    go_in = serializers.BooleanField()
    date = serializers.DateTimeField()

    class Meta:
        read_only_fields = ('enabled', 'lost_date')


class CheckInCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckIn
        fields = ('__all__')
        read_only_fields = ('date', 'enabled', 'seat', 'worker')


class TypeItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeItem
        fields = ('__all__')
        read_only_fields = ('enabled', 'company',)


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('__all__')
        read_only_fields = ('enabled', 'company', 'type_item',)


class RegisterItem(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('__all__')
        read_only_fields = ('registered_by', 'enabled',
                            'lost', 'lost_date', 'seat_registration')


class RegisterItemTest(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('type_item',
                  'owner',
                  'brand',
                  'reference',
                  'color',
                  'description',
                  'lost',
                  'enabled',
                  'seat_registration',
                  'registration_date',
                  'registered_by')
        read_only_fields = ('enabled', 'lost_date')


class LostItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    description = serializers.CharField(max_length=255)
    reference = serializers.CharField(max_length=30)
    color = serializers.CharField(max_length=30)
    type_item = serializers.CharField(max_length=30)
    owner_name = serializers.CharField(max_length=50)
    owner_last_name = serializers.CharField(max_length=50)
    owner_dni = serializers.CharField(max_length=30)
    item_brand = serializers.CharField(max_length=30)
    lost = serializers.BooleanField(default=False)
    lost_date = serializers.DateTimeField()
    lost_in_seat = serializers.CharField(max_length=100)
    lost_in_seat_id = serializers.IntegerField()
    owner_email = serializers.EmailField()
    owner_phone = serializers.CharField(max_length=20)

    class Meta:
        fields = ('__all__')
        model = LostItem
