import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "created_at": ["gte", "lte"],
            "phone": ["startswith"],
        }


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["icontains"],
            "price": ["gte", "lte"],
            "stock": ["exact", "gte", "lte"],
        }


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "total_amount": ["gte", "lte"],
            "order_date": ["gte", "lte"],
            "customer__name": ["icontains"],
            "products__name": ["icontains"],
        }


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        customer = Customer(name=name, email=email, phone=phone)
        customer.full_clean()
        customer.save()
        return CreateCustomer(
            customer=customer, message="Customer created successfully"
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for i, data in enumerate(input):
                try:
                    name = data["name"]
                    email = data["email"]
                    phone = data.get("phone", None)

                    if Customer.objects.filter(email=email).exists():
                        raise ValidationError("Email already exists")

                    customer = Customer(name=name, email=email, phone=phone)
                    customer.full_clean()
                    customer.save()
                    created_customers.append(customer)

                except Exception as e:
                    errors.append(f"Entry {i + 1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.full_clean()
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        if not product_ids:
            raise ValidationError("At least one product must be selected")

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = list(Product.objects.filter(pk__in=product_ids))
        if len(products) != len(product_ids):
            raise ValidationError("One or more product IDs are invalid")

        total_amount = sum(p.price for p in products)

        with transaction.atomic():
            order = Order(
                customer=customer,
                total_amount=total_amount,
                order_date=order_date or timezone.now(),
            )
            order.save()
            order.products.set(products)

        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(graphene.String)
    message = graphene.String()

    def mutate(self, info):
        low_stock = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock:
            product.stock += 10
            product.save()
            updated.append(product.name)
        return UpdateLowStockProducts(
            updated_products=updated,
            message="Low-stock products restocked"
        )


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerType, filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType, filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
