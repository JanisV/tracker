from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect

from .forms import AuctionForm
from .models import Auction
from .models import Completion


def index(request):
    return render(
        request,
        'index.html'
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
