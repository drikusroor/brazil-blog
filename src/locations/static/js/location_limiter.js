// static/js/location_limiter.js
document.addEventListener('DOMContentLoaded', function () {

    // observe the amount of children in id='id_location-FORMS'
    // and disable the add location button if there is 1 child
    // and enable the add location button if there are 0 children
    const locationForms = document.getElementById('id_location-FORMS');
    const addLocationButton = document.getElementById('id_location-ADD');

    function checkLocationForms() {
        if (!addLocationButton) {
            console.warn('Add location button not found');
            return;
        }

        const children = Array.from(locationForms.children).filter((child) => !child.classList.contains('deleted'));

        if (children.length >= 1) {
            addLocationButton.disabled = true;
            addLocationButton.setAttribute('title', 'Only one location is allowed');
        } else {
            addLocationButton.disabled = false;
            addLocationButton.setAttribute('title', 'Add another location');
        }

        // Mark the extra location as 'extra' to be removed
        if (children.length > 1) {    
            children.forEach(function (locationForm, index) {

                // Skip the first location form
                if (index === 0) {
                    return;
                }

                if (!locationForm.classList.contains('deleted')) {
                    locationForm.classList.add('deleted');
                    locationForm.style.display = 'none';
                }
            });
        }
    }

    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList') {
                checkLocationForms();
            }
        });
    });

    // Check the initial amount of children
    checkLocationForms();

    observer.observe(locationForms, { childList: true });
});