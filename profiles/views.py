from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import UserProfile
from .forms import UserProfileForm, CustomUserUpdateForm
from catalogue.models import DigitalDownload


@login_required
def profile(request):
    """Display the user's profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, "Profile created successfully!")

    if request.method == "POST":
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()
                profile_instance = profile_form.save(commit=False)
                if not request.FILES.get("profile_image"):
                    profile_instance.profile_image = profile.profile_image
                profile_instance.save()
                profile.refresh_from_db()
                messages.success(request, "Profile updated successfully!")
            except Exception as e:
                messages.error(
                    request,
                    f"Error saving profile: {str(e)}"
                )
        else:
            if not user_form.is_valid():
                messages.error(
                    request,
                    "User information has errors. Please check the form.",
                )
            if not profile_form.is_valid():
                messages.error(
                    request,
                    "Profile information has errors. Please check the form.",
                )
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    orders = request.user.orders.all().order_by("-date")

    purchased_products = []
    for order in orders:
        for line_item in order.lineitems.all():
            try:
                digital_download = line_item.product.digital_download
                purchased_products.append({
                    "product": line_item.product,
                    "download": digital_download,
                    "license_type": line_item.license_type,
                    "order_date": order.date,
                    "order_number": order.order_number,
                })
            except DigitalDownload.DoesNotExist:
                continue

    context = {
        "profile": profile,
        "user_form": user_form,
        "profile_form": profile_form,
        "orders": orders,
        "purchased_products": purchased_products,
        "on_profile_page": True,
    }

    return render(request, "profiles/profile.html", context)


@login_required
def delete_account(request):
    """Handle account deletion with confirmation."""
    if request.method == "POST":
        if "confirm_delete" in request.POST:
            try:
                username = request.user.username
                email = request.user.email

                request.user.delete()
                logout(request)

                messages.success(
                    request,
                    (
                        f"Account for {username} ({email}) has been "
                        "permanently deleted."
                    ),
                )
                return redirect("home")
            except Exception as e:
                messages.error(
                    request,
                    f"Error deleting account: {str(e)}"
                )
        else:
            messages.warning(request, "Account deletion cancelled.")
            return redirect("profile")

    return render(
        request,
        "profiles/delete_account.html",
        {"on_profile_page": True}
    )
