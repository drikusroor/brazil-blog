// static/js/map_picker.js
document.addEventListener("DOMContentLoaded", function () {
  const mapElements = document.querySelectorAll(".map-picker-widget");

  mapElements.forEach(function (element) {
    return handleMapElement(element);
  });
});

document.addEventListener("w-formset:added", function (event) {
  const mapElements = event.target.querySelectorAll(".map-picker-widget");

  mapElements.forEach(function (element) {
    return handleMapElement(element);
  });
});

function handleMapElement(element) {
  const input = element.querySelector("input");
  const mapElement = element.querySelector('div[id^="map-"]');
  const latitudeFieldName = input.getAttribute("latitude_field_name");
  const longitudeFieldName = input.getAttribute("longitude_field_name");
  const modelName = input.getAttribute("model_name");
  const currentLocationButton = element.querySelector(
    "[data-button-current-location]"
  );

  if (!mapElement) {
    console.error("Map container not found");
    return;
  }

  let map;
  let marker;

  function initializeMap() {
    // remove existing map
    if (map) {
      map.remove();
    }

    // remove marker
    if (marker) {
      marker.remove();
      marker = null;
    }

    map = L.map(mapElement).setView([0, 0], 2);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    // Initialize marker if value exists
    if (input.value) {
      const [lat, lng] = input.value.split(",");
      updateMarker(parseFloat(lat), parseFloat(lng));
    }

    map.on("click", function (e) {
      updateMarker(e.latlng.lat, e.latlng.lng);
    });
  }

  function updateMarker(lat, lng) {
    // Validate latitude and longitude
    // and make sure they are numbers that have a maximum of 6 decimal places
    // Latitude must be a number between -90 and 90
    // Longitude must be a number between -180 and 180
    if (
      isNaN(lat) ||
      isNaN(lng) ||
      lat < -90 ||
      lat > 90 ||
      lng < -180 ||
      lng > 180
    ) {
      console.error("Invalid latitude or longitude");
      return;
    }

    // Round to 6 decimal places
    lat = parseFloat(lat.toFixed(6));
    lng = parseFloat(lng.toFixed(6));

    // Update input fields
    if (latitudeFieldName && longitudeFieldName) {
      // id_location-FORMS aka id_{modelName}-FORMS
      const container = modelName
        ? document.getElementById(`id_${modelName}-FORMS`)
        : document;
      const children = Array.from(container.children).filter((child) => {
        return !child.classList.contains("deleted");
      });

      let child = children[0];

      // Find the latitude and longitude input fields, there might be multiple
      // so we need to find the one that is inside the subform and is not marked as deleted
      let latitudeInput = child?.querySelector(
        `input[name="${latitudeFieldName}"]`
      );
      let longitudeInput = child?.querySelector(
        `input[name="${longitudeFieldName}"]`
      );

      if (!latitudeInput || !longitudeInput) {
        // look for *-latitude and *-longitude fields
        latitudeInput = child?.querySelector(`input[name*="-latitude"]`);
        longitudeInput = child?.querySelector(`input[name*="-longitude"]`);
      }

      if (!latitudeInput || !longitudeInput) {
        console.warn("Latitude and/or longitude field names not set");

        // Check if add location button exists, with id of 'id_location-ADD'
        const addLocationButton = document.querySelector(
          `button[id^="id_${modelName}-ADD"]`
        );

        if (!addLocationButton) {
          console.warn("Add location button not found");
          return;
        }

        // Click the add location button
        addLocationButton.click();

        // Find the new child
        child = Array.from(container.children).find(
          (child) => !child.classList.contains("deleted")
        );

        latitudeInput = child?.querySelector(`input[name*="-latitude"]`);
        longitudeInput = child?.querySelector(`input[name*="-longitude"]`);
      }

      if (latitudeInput && longitudeInput) {
        latitudeInput.value = lat;
        longitudeInput.value = lng;
      }

      const locationNameInput = child?.querySelector('input[name*="-name"]');
      if (locationNameInput && !locationNameInput.value) {
        locationNameInput.focus();
      }
    }

    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      marker = L.marker([lat, lng]).addTo(map);
    }
    map.setView([lat, lng], 10);
    input.value = lat + "," + lng;
  }

  // Find the parent tabpanel
  let tabPanel = mapElement.closest('[role="tabpanel"]');

  if (tabPanel) {
    // Initialize map if the tab is initially visible
    if (!tabPanel.hasAttribute("hidden")) {
      initializeMap();
    }

    // Use MutationObserver to detect when the tab becomes visible
    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (
          mutation.type === "attributes" &&
          mutation.attributeName === "hidden"
        ) {
          if (!tabPanel.hasAttribute("hidden")) {
            initializeMap();
            if (map) {
              map.invalidateSize();
            }
          }
        }
      });
    });

    observer.observe(tabPanel, {
      attributes: true,
      attributeFilter: ["hidden"],
    });
  } else {
    // If not in a tab, initialize immediately
    initializeMap();
  }

  if (currentLocationButton) {
    currentLocationButton.addEventListener("click", () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
          updateMarker(position.coords.latitude, position.coords.longitude);
        }, (error) => {
          // show user a message that there was an error getting current location
          alert(`Error getting current location from browser: ${error.message}`);
          console.error("Error getting current location", error);
        });
      } else {
        // show user a message that geolocation is not supported
        alert("Geolocation is not supported by this browser.");
        console.error("Geolocation is not supported by this browser.");
      }
    });
  }
}

window.handleMapElement = handleMapElement;