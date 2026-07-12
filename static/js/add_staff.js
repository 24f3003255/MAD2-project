const { createApp } = Vue

createApp({
    data() {
        return {
            username: "",
            email: "",
            password: "",
            contact_number: "",
            successMessage: "",
            errorMessage: ""
        }
    },
    mounted() {
        const token = localStorage.getItem("token")
        const userRole = localStorage.getItem("role")
        if (!token || userRole !== "Admin") {
            window.location = "/"
        }
    },
    methods: {
        async addStaff() {
            this.successMessage = ""
            this.errorMessage = ""
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/add_staff", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    username: this.username,
                    email: this.email,
                    password: this.password,
                    contact_number: this.contact_number
                })
            })
            const result = await response.json()
            if (response.ok) {
                this.successMessage = result.message
                this.username = ""
                this.email = ""
                this.password = ""
                this.contact_number = ""
            }
            else {
                this.errorMessage = result.message
            }
        },
        goBack() {
            window.location = "/admin"
        }
    }
}).mount("#app")