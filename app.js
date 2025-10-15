// TripLens Dashboard Application
class TripLensApp {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.tripsData = [];
        this.filteredData = [];
        this.charts = {};
        
        this.init();
    }

    async init() {
        this.showLoading();
        
        // Initialize event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadData();
        await this.loadMetrics();
        await this.loadAnalytics();
        
        // Initialize charts
        this.initializeCharts();
        
        // Populate dashboard
        this.updateDashboard();
        
        this.hideLoading();
    }

    setupEventListeners() {
        // Date range picker
        const applyFilterBtn = document.querySelector('.btn-primary');
        applyFilterBtn.addEventListener('click', () => this.applyDateFilter());

        // Search functionality
        const searchInput = document.getElementById('trip-search');
        searchInput.addEventListener('input', (e) => this.filterTrips(e.target.value));

        // Vendor filter
        const vendorFilter = document.querySelector('.filter-select');
        vendorFilter.addEventListener('change', (e) => this.filterByVendor(e.target.value));

        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => this.previousPage());
        document.getElementById('next-page').addEventListener('click', () => this.nextPage());

        // Chart controls
        const chartSelect = document.querySelector('.chart-select');
        chartSelect.addEventListener('change', (e) => this.updateTripTrendsChart(e.target.value));
    }

    async loadData() {
        try {
            // Try to fetch from API server
            const response = await fetch('http://localhost:5000/api/trips');
            if (response.ok) {
                const data = await response.json();
                this.tripsData = data.trips || [];
                console.log('✓ Data loaded from API');
            } else {
                throw new Error('API not available');
            }
        } catch (error) {
            console.log('⚠️ API not available, using mock data for demonstration');
            this.tripsData = this.generateMockData();
        }
        
        this.filteredData = [...this.tripsData];
    }

    async loadMetrics() {
        try {
            const response = await fetch('http://localhost:5000/api/metrics');
            if (response.ok) {
                this.metricsData = await response.json();
                console.log('✓ Metrics loaded from API');
            } else {
                throw new Error('Metrics API not available');
            }
        } catch (error) {
            console.log('⚠️ Using calculated metrics from trip data');
            this.metricsData = null;
        }
    }

    async loadAnalytics() {
        try {
            const [trendsResponse, vendorsResponse] = await Promise.all([
                fetch('http://localhost:5000/api/analytics/trends'),
                fetch('http://localhost:5000/api/analytics/vendors')
            ]);
            
            if (trendsResponse.ok && vendorsResponse.ok) {
                this.trendsData = await trendsResponse.json();
                this.vendorsData = await vendorsResponse.json();
                console.log('✓ Analytics data loaded from API');
            } else {
                throw new Error('Analytics API not available');
            }
        } catch (error) {
            console.log('⚠️ Using mock analytics data');
            this.trendsData = null;
            this.vendorsData = null;
        }
    }

    generateMockData() {
        const vendors = [
            { id: 1, name: 'Yego Taxi' },
            { id: 2, name: 'SafeBoda' }
        ];
        
        const statuses = ['completed', 'pending', 'cancelled'];
        const mockTrips = [];
        
        for (let i = 0; i < 100; i++) {
            const vendor = vendors[Math.floor(Math.random() * vendors.length)];
            const pickupDate = new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
            const duration = Math.floor(Math.random() * 60) + 5; // 5-65 minutes
            const dropoffDate = new Date(pickupDate.getTime() + duration * 60000);
            
            mockTrips.push({
                id: `id${Math.random().toString(36).substr(2, 7)}`,
                vendor_id: vendor.id,
                vendor_name: vendor.name,
                pickup_date: pickupDate.toISOString(),
                dropoff_date: dropoffDate.toISOString(),
                passenger_count: Math.floor(Math.random() * 6) + 1,
                trip_duration: duration,
                status: statuses[Math.floor(Math.random() * statuses.length)],
                pickup_longitude: -73.9 + (Math.random() - 0.5) * 0.1,
                pickup_latitude: 40.7 + (Math.random() - 0.5) * 0.1,
                dropoff_longitude: -73.9 + (Math.random() - 0.5) * 0.1,
                dropoff_latitude: 40.7 + (Math.random() - 0.5) * 0.1
            });
        }
        
        return mockTrips;
    }

    initializeCharts() {
        this.initializeTripTrendsChart();
        this.initializeVendorChart();
    }

    initializeTripTrendsChart() {
        const ctx = document.getElementById('tripTrendsChart').getContext('2d');
        
        // Generate sample data for the last 7 days
        const labels = [];
        const tripCounts = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
            tripCounts.push(Math.floor(Math.random() * 50) + 20);
        }
        
        this.charts.tripTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Trips',
                    data: tripCounts,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initializeVendorChart() {
        const ctx = document.getElementById('vendorChart').getContext('2d');
        
        this.charts.vendor = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Yego Taxi', 'SafeBoda'],
                datasets: [{
                    data: [65, 35],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    updateDashboard() {
        this.updateMetrics();
        this.updateTripsTable();
    }

    updateMetrics() {
        let totalTrips, totalPassengers, avgDuration, estimatedRevenue;
        
        if (this.metricsData) {
            // Use API data
            totalTrips = this.metricsData.total_trips;
            totalPassengers = this.metricsData.total_passengers;
            avgDuration = Math.round(this.metricsData.avg_duration);
            estimatedRevenue = this.metricsData.estimated_revenue;
        } else {
            // Calculate from filtered data
            totalTrips = this.filteredData.length;
            totalPassengers = this.filteredData.reduce((sum, trip) => sum + trip.passenger_count, 0);
            avgDuration = this.filteredData.length > 0 
                ? Math.round(this.filteredData.reduce((sum, trip) => sum + trip.trip_duration, 0) / this.filteredData.length)
                : 0;
            estimatedRevenue = totalTrips * 15; // Assuming $15 per trip average
        }

        document.getElementById('total-trips').textContent = totalTrips.toLocaleString();
        document.getElementById('total-passengers').textContent = totalPassengers.toLocaleString();
        document.getElementById('avg-duration').textContent = `${avgDuration} min`;
        document.getElementById('revenue').textContent = `$${estimatedRevenue.toLocaleString()}`;
    }

    updateTripsTable() {
        const tbody = document.getElementById('trips-table-body');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);

        tbody.innerHTML = pageData.map(trip => `
            <tr>
                <td>${trip.id}</td>
                <td>${trip.vendor_name}</td>
                <td>${new Date(trip.pickup_date).toLocaleString()}</td>
                <td>${trip.trip_duration} min</td>
                <td>${trip.passenger_count}</td>
                <td><span class="status-badge ${trip.status}">${trip.status}</span></td>
                <td>
                    <button class="btn btn-outline" onclick="app.viewTripDetails('${trip.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        this.updatePagination();
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
        const pageInfo = document.querySelector('.page-info');
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;

        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
    }

    filterTrips(searchTerm) {
        this.filteredData = this.tripsData.filter(trip => 
            trip.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            trip.vendor_name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.currentPage = 1;
        this.updateDashboard();
    }

    filterByVendor(vendorId) {
        if (vendorId === 'all') {
            this.filteredData = [...this.tripsData];
        } else {
            this.filteredData = this.tripsData.filter(trip => trip.vendor_id == vendorId);
        }
        this.currentPage = 1;
        this.updateDashboard();
    }

    applyDateFilter() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        if (startDate && endDate) {
            this.filteredData = this.tripsData.filter(trip => {
                const tripDate = new Date(trip.pickup_date);
                return tripDate >= new Date(startDate) && tripDate <= new Date(endDate);
            });
        } else {
            this.filteredData = [...this.tripsData];
        }
        
        this.currentPage = 1;
        this.updateDashboard();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updateTripsTable();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.updateTripsTable();
        }
    }

    updateTripTrendsChart(period) {
        // Update chart based on selected period
        console.log(`Updating chart for period: ${period}`);
        // Implementation would fetch new data based on period
    }

    viewTripDetails(tripId) {
        const trip = this.tripsData.find(t => t.id === tripId);
        if (trip) {
            alert(`Trip Details:\nID: ${trip.id}\nVendor: ${trip.vendor_name}\nDuration: ${trip.trip_duration} min\nPassengers: ${trip.passenger_count}`);
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TripLensApp();
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TripLensApp;
}
