from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.utils import formats
from easy_thumbnails.files import get_thumbnailer

from .forms import AuctionForm
from .models import Auction
from .models import Completion
from .models import Raw
from .grabber import Grabber


def index(request):
    return render(
        request,
        'index.html',
        {'completeon': Completion.objects.all()}
    )


def new(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST)
        if form.is_valid():
            added = 0
            site = request.POST['site']
            from_num = int(request.POST['from_num'])
            till_num = int(request.POST['till_num'])
            for i in range(from_num, till_num + 1):
                auc = Auction.objects.get_or_create(number=i, site_id=site)[0]

                for cat in request.POST.getlist('categories'):
                    new = Completion.objects.get_or_create(auction=auc, category_id=cat)[1]
                    if new:
                        added += 1

            if added:
                msg = "Added %d" % added
            else:
                msg = "Nothing added"
            messages.info(request, msg)

            return redirect('index')

    else:
        form = AuctionForm()

    return render(
        request,
        'new.html',
        {'form': form}
    )


class CompletionTableJson(BaseDatatableView):
    model = Completion

    # define the columns that will be returned
    columns = ['id', 'status', 'total', 'processed', 'auction', 'category', 'created_at', 'updated_at']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'status', 'total', 'processed', 'auction', 'category', 'created_at', 'updated_at']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'created_at':
            return formats.date_format(row.created_at, "SHORT_DATETIME_FORMAT")
        elif column == 'updated_at':
            return formats.date_format(row.updated_at, "SHORT_DATETIME_FORMAT")
        else:
            return super().render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(category__title__istartswith=search)

        return qs


def raw(request):
    return render(
        request,
        'raw.html'
    )


class RawTableJson(BaseDatatableView):
    model = Raw

    columns = ['url', 'auction', 'category', 'photo']
    order_columns = ['url', 'auction', 'category', '']

    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'photo':
            photos = row.photos.all()
            if photos:
                try:
                    thumb_url = get_thumbnailer(photos[0].file)['thumbnail'].url
                except:
                    thumb_url = photos[0].file.url
                return [thumb_url, photos[0].file.url]
            else:
                return ''
        else:
            return super().render_column(row, column)


def run(request):
    competeon = Completion.objects.filter(status='n').first()
    if competeon:
        grabber = Grabber(competeon)
        grabber.run()

    return redirect('index')
