const { createApp } = Vue;
createApp({
    data() {
        return {
            users: [],
            allUsers: [],
            searchQuery: ""
        };
    },
    mounted() {
        this.loadUsers();
    },
    methods: {
        async loadUsers() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/admin/users", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            this.users = data;
            this.allUsers = data;
        },
        searchUsers() {
            const search = this.searchQuery.toLowerCase().trim();
            if (search === "") {
                this.users = this.allUsers;
                return;
            }
            this.users = this.allUsers.filter(user =>
                user.username.toLowerCase().includes(search) ||
                user.email.toLowerCase().includes(search) ||
                String(user.id).includes(search)
            );
        },
        goToDashboard() {
            window.location.href = "/admin";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        },
        async deactivateUser(userId) {
            const confirmDeactivate = confirm("Are you sure you want to deactivate this user?");
            if (!confirmDeactivate) return;
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/admin/user/${userId}/deactivate`, {
                method: "PUT",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            const data = await response.json();
            alert(data.message);
            if (response.ok) {
                this.loadUsers();
            }
        }
    }
}).mount("#app");