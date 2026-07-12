const { createApp } = Vue

createApp({
    data() {
        return {
            trek_name: "",
            location: "",
            difficulty: "",
            duration: "",
            available_slots: "",
            assigned_staff_id: "",
            status: "Pending",
            start_date: "",
            end_date: "",
            description: "",
            staffOptions: []
        }
    },
    mounted() {
        this.loadStaffOptions()
    },
    methods: {
        async loadStaffOptions() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/staff-options", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            this.staffOptions = await response.json()
        },
        async addTrek() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/treks", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    trek_name: this.trek_name,
                    location: this.location,
                    difficulty: this.difficulty,
                    duration: this.duration,
                    available_slots: this.available_slots,
                    assigned_staff_id: this.assigned_staff_id,
                    status: this.status,
                    start_date: this.start_date,
                    end_date: this.end_date,
                    description: this.description
                })
            })
            const result = await response.json()
            alert(result.message)
            if (response.ok) {
                window.location = "/admin/manage-treks"
            }
        },
        goToDashboard() {
            window.location = "/admin"
        },
        logout() {
            localStorage.removeItem("token")
            localStorage.removeItem("role")
            window.location = "/"
        }
    }
}).mount("#app")