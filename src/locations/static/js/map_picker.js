// static/js/map_picker.js
document.addEventListener('DOMContentLoaded', function() {
    const mapElements = document.querySelectorAll('.map-picker-widget');
    
    mapElements.forEach(function(element) {
        const input = element.querySelector('input');
        const mapElement = element.querySelector('div[id^="map-"]');
        const latitudeFieldName = input.getAttribute('latitude_field_name');
        const longitudeFieldName = input.getAttribute('longitude_field_name');
        
        if (!mapElement) {
            console.error('Map container not found');
            return;
        }

        const map = L.map(mapElement).setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        let marker;
        
        function updateMarker(lat, lng) {
            // Update input fields
            if (latitudeFieldName && longitudeFieldName) {
                let latitudeInput = document.querySelector(`input[name="${latitudeFieldName}"]`);
                let longitudeInput = document.querySelector(`input[name="${longitudeFieldName}"]`);

                if (!latitudeInput || !longitudeInput) {
                    // look for *-latitude and *-longitude fields
                    latitudeInput = document.querySelector(`input[name*="-latitude"]`);
                    longitudeInput = document.querySelector(`input[name*="-longitude"]`);
                }

                console.log({latitudeInput, longitudeInput});

                if (latitudeInput && longitudeInput) {
                    latitudeInput.value = lat;
                    longitudeInput.value = lng;
                }
            }

            if (marker) {
                marker.setLatLng([lat, lng]);
            } else {
                marker = L.marker([lat, lng]).addTo(map);
            }
            map.setView([lat, lng], 10);
            input.value = lat + ',' + lng;
        }
        
        // Initialize marker if value exists
        if (input.value) {
            const [lat, lng] = input.value.split(',');
            updateMarker(parseFloat(lat), parseFloat(lng));
        }
        
        map.on('click', function(e) {
            updateMarker(e.latlng.lat, e.latlng.lng);
        });
    });
});