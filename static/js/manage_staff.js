const { createApp } = Vue

createApp({
    data() {
        return {
            staffs: [],
            allStaffs: [],
            searchQuery: ""
        }
    },
    mounted() {
        const token = localStorage.getItem("token")
        const userRole = localStorage.getItem("role")
        if (!token || userRole !== "Admin") {
            window.location = "/"
            return
        }
        this.loadStaffs()
    },
    methods: {
        async loadStaffs() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/staffs", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            if (!response.ok) {
                alert(result.message || "Unable to load staff list")
                return
            }
            this.staffs = result
            this.allStaffs = result
        },
        searchStaff() {
            const search = this.searchQuery.toLowerCase().trim()
            if (!search) {
                this.staffs = this.allStaffs
                return
            }
            this.staffs = this.allStaffs.filter(staff =>
                String(staff.id).includes(search) ||
                staff.username.toLowerCase().includes(search) ||
                staff.email.toLowerCase().includes(search)
            )
        },
        async deactivateStaff(staffId) {
            if (!confirm("Deactivate this staff member?")) {
                return
            }
            const token = localStorage.getItem("token")
            const response = await fetch(`/api/admin/staff/${staffId}/deactivate`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            alert(result.message)
            if (response.ok) {
                this.loadStaffs()
            }
        },
        goToDashboard() {
            window.location = "/admin"
        },
        goToAddStaff() {
            window.location = "/admin/add-staff"
        },
        logout() {
            localStorage.removeItem("token")
            localStorage.removeItem("role")
            localStorage.removeItem("username")
            window.location = "/"
        }
    }
}).mount("#app")