// API 基礎設定
const API_BASE_URL = 'http://localhost:8070';

// API 服務類別
const api = {
    // 認證相關
    async login(email, password, login_as = 'member') {
        const response = await axios.post(`${API_BASE_URL}/login`, {
            email,
            password,
            login_as
        });
        return response.data;
    },

    async register(name, email, password) {
        const response = await axios.post(`${API_BASE_URL}/register`, {
            name,
            email,
            password
        });
        return response.data;
    },

    // 物品相關
    async getItemDetail(i_id) {
        const response = await axios.get(`${API_BASE_URL}/item/${i_id}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getCategoryItems(c_id) {
        const response = await axios.get(`${API_BASE_URL}/item/category/${c_id}`);
        return response.data;
    },

    async getItemBorrowedTime(i_id) {
        const response = await axios.get(`${API_BASE_URL}/item/${i_id}/borrowed_time`);
        return response.data;
    },

    async uploadItem(data) {
        const response = await axios.post(`${API_BASE_URL}/item/upload`, data, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async updateItem(i_id, data) {
        const response = await axios.put(`${API_BASE_URL}/item/${i_id}`, data, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async reportItem(i_id, comment) {
        const response = await axios.post(`${API_BASE_URL}/item/${i_id}/report`, { comment }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async verifyItem(i_id) {
        const response = await axios.post(`${API_BASE_URL}/item/${i_id}/verify`, {}, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    // 個人資料相關
    async getProfile() {
        const response = await axios.get(`${API_BASE_URL}/me/profile`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getMyItems() {
        const response = await axios.get(`${API_BASE_URL}/me/items`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getMyReservations() {
        const response = await axios.get(`${API_BASE_URL}/me/reservations`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getReservationDetail(r_id) {
        const response = await axios.get(`${API_BASE_URL}/me/reservation_detail/${r_id}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getReviewableItems() {
        const response = await axios.get(`${API_BASE_URL}/me/reviewable_items`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async reviewItem(l_id, score, comment) {
        const response = await axios.post(`${API_BASE_URL}/me/review_item/${l_id}`, {
            score,
            comment
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getContributions() {
        const response = await axios.get(`${API_BASE_URL}/me/contributions`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    // 物主相關
    async getFutureReservationDetails() {
        const response = await axios.get(`${API_BASE_URL}/owner/future_reservation_details`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async punchInLoan(l_id, event_type) {
        const response = await axios.post(`${API_BASE_URL}/owner/punch_in_loan/${l_id}`, {
            event_type
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    // 預約相關
    async createReservation(rd_list) {
        const response = await axios.post(`${API_BASE_URL}/reservation/create`, {
            rd_list
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async deleteReservation(r_id) {
        const response = await axios.delete(`${API_BASE_URL}/reservation/delete/${r_id}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    // 員工相關
    async getStaff() {
        const response = await axios.get(`${API_BASE_URL}/staff`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getNotDealReports() {
        const response = await axios.get(`${API_BASE_URL}/staff/report`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async concludeReport(re_id, r_conclusion) {
        const response = await axios.post(`${API_BASE_URL}/staff/report/${re_id}`, {
            r_conclusion
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async getNotDealVerification() {
        const response = await axios.get(`${API_BASE_URL}/staff/verification`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    },

    async concludeVerification(iv_id, v_conclusion) {
        const response = await axios.post(`${API_BASE_URL}/staff/verification/${iv_id}`, {
            v_conclusion
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return response.data;
    }
};

// Vue 應用程式
const { createApp } = Vue;

createApp({
    data() {
        return {
            // 認證狀態
            isLoggedIn: false,
            userRole: '',
            userName: '',
            token: '',
            
            // 表單資料
            loginForm: {
                email: '',
                password: '',
                login_as: 'member'
            },
            registerForm: {
                name: '',
                email: '',
                password: ''
            },
            showLogin: true,
            
            // 視圖控制
            currentView: 'home',
            
            // 資料
            myItems: [],
            browseItems: [],
            myReservations: [],
            reviewableItems: [],
            contributions: [],
            bans: [],
            verifications: [],
            reports: [],
            categories: [],
            selectedCategory: '',
            
            // 表單
            uploadForm: {
                i_name: '',
                description: '',
                out_duration: '',
                c_id: '',
                p_id_list_str: ''
            },
            editForm: {
                i_id: null,
                i_name: '',
                description: '',
                out_duration: '',
                c_id: '',
                p_id_list_str: ''
            },
            reservationForm: {
                rd_list: [{
                    i_id: '',
                    p_id: '',
                    est_start_at: '',
                    est_due_at: ''
                }]
            },
            reviewForm: {
                l_id: null,
                score: 5,
                comment: ''
            },
            
            // UI 狀態
            loading: false,
            errorMessage: '',
            successMessage: '',
            showUploadModal: false,
            showEditModal: false,
            showReservationModal: false,
            showReviewModalFlag: false,
            recordsTab: 'reservations',
            currentReservationItem: null
        };
    },
    
    mounted() {
        // 檢查是否有儲存的 token
        const savedToken = localStorage.getItem('token');
        const savedRole = localStorage.getItem('role');
        const savedName = localStorage.getItem('userName');
        
        if (savedToken) {
            this.token = savedToken;
            this.userRole = savedRole;
            this.userName = savedName;
            this.isLoggedIn = true;
        }
    },
    
    methods: {
        // 認證相關
        async handleLogin() {
            try {
                this.loading = true;
                this.errorMessage = '';
                const result = await api.login(
                    this.loginForm.email,
                    this.loginForm.password,
                    this.loginForm.login_as
                );
                
                if (result.token) {
                    this.token = result.token;
                    this.userRole = result.role;
                    this.userName = result.m_name || result.s_name;
                    this.isLoggedIn = true;
                    
                    // 儲存到 localStorage
                    localStorage.setItem('token', result.token);
                    localStorage.setItem('role', result.role);
                    localStorage.setItem('userName', this.userName);
                    
                    this.currentView = 'home';
                    this.showSuccess('登入成功！');
                }
            } catch (error) {
                this.errorMessage = error.response?.data?.error || '登入失敗';
            } finally {
                this.loading = false;
            }
        },
        
        async handleRegister() {
            try {
                this.loading = true;
                this.errorMessage = '';
                const result = await api.register(
                    this.registerForm.name,
                    this.registerForm.email,
                    this.registerForm.password
                );
                
                if (result.m_id) {
                    this.showSuccess('註冊成功！請登入');
                    this.showLogin = true;
                    // 清空註冊表單
                    this.registerForm = { name: '', email: '', password: '' };
                }
            } catch (error) {
                this.errorMessage = error.response?.data?.error || '註冊失敗';
            } finally {
                this.loading = false;
            }
        },
        
        logout() {
            this.isLoggedIn = false;
            this.userRole = '';
            this.userName = '';
            this.token = '';
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            localStorage.removeItem('userName');
            this.currentView = 'home';
            this.showSuccess('已登出');
        },
        
        showProfile() {
            alert(`使用者名稱: ${this.userName}\n角色: ${this.userRole === 'member' ? '會員' : '員工'}`);
        },
        
        goToHome() {
            if (this.isLoggedIn) {
                this.currentView = 'home';
            }
        },
        
        // 物品管理 (Member)
        async loadMyItems() {
            try {
                this.loading = true;
                const result = await api.getMyItems();
                this.myItems = result.items || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async handleUploadItem() {
            try {
                this.loading = true;
                const p_id_list = this.uploadForm.p_id_list_str.split(',').map(id => parseInt(id.trim()));
                const data = {
                    i_name: this.uploadForm.i_name,
                    description: this.uploadForm.description,
                    out_duration: parseInt(this.uploadForm.out_duration),
                    c_id: parseInt(this.uploadForm.c_id),
                    p_id_list: p_id_list
                };
                
                await api.uploadItem(data);
                this.showUploadModal = false;
                this.uploadForm = { i_name: '', description: '', out_duration: '', c_id: '', p_id_list_str: '' };
                this.showSuccess('物品上傳成功！');
                await this.loadMyItems();
            } catch (error) {
                this.showError(error.response?.data?.error || '上傳失敗');
            } finally {
                this.loading = false;
            }
        },
        
        editItem(item) {
            this.editForm = {
                i_id: item.i_id,
                i_name: item.i_name,
                description: item.description,
                out_duration: item.out_duration,
                c_id: item.c_id,
                p_id_list_str: '' // 這裡應該從資料庫取得，暫時留空
            };
            this.showEditModal = true;
        },
        
        async handleUpdateItem() {
            try {
                this.loading = true;
                const data = {};
                if (this.editForm.i_name) data.i_name = this.editForm.i_name;
                if (this.editForm.description) data.description = this.editForm.description;
                if (this.editForm.out_duration) data.out_duration = parseInt(this.editForm.out_duration);
                if (this.editForm.c_id) data.c_id = parseInt(this.editForm.c_id);
                if (this.editForm.p_id_list_str) {
                    data.p_id_list = this.editForm.p_id_list_str.split(',').map(id => parseInt(id.trim()));
                }
                
                await api.updateItem(this.editForm.i_id, data);
                this.showEditModal = false;
                this.showSuccess('物品更新成功！');
                await this.loadMyItems();
            } catch (error) {
                this.showError(error.response?.data?.error || '更新失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async removeItem(item) {
            if (!confirm(`確定要下架「${item.i_name}」嗎？`)) return;
            
            try {
                this.loading = true;
                await api.updateItem(item.i_id, { status: 'Not reservable' });
                this.showSuccess('物品已下架');
                await this.loadMyItems();
            } catch (error) {
                this.showError(error.response?.data?.error || '下架失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async verifyItem(i_id) {
            try {
                this.loading = true;
                await api.verifyItem(i_id);
                this.showSuccess('已申請審核');
                await this.loadMyItems();
            } catch (error) {
                this.showError(error.response?.data?.error || '申請失敗');
            } finally {
                this.loading = false;
            }
        },
        
        // 瀏覽物品 (Member)
        async loadCategoryItems() {
            if (!this.selectedCategory) {
                this.browseItems = [];
                return;
            }
            
            try {
                this.loading = true;
                const result = await api.getCategoryItems(this.selectedCategory);
                this.browseItems = result.items || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async viewItemDetail(i_id) {
            try {
                const result = await api.getItemDetail(i_id);
                alert(`物品名稱: ${result.item.i_name}\n狀態: ${result.item.status}\n描述: ${result.item.description}\n外借時長: ${result.item.out_duration} 天`);
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            }
        },
        
        addToReservationList(item) {
            this.currentReservationItem = item;
            this.reservationForm.rd_list = [{
                i_id: item.i_id,
                p_id: '',
                est_start_at: '',
                est_due_at: ''
            }];
            this.showReservationModal = true;
        },
        
        addReservationItem() {
            this.reservationForm.rd_list.push({
                i_id: '',
                p_id: '',
                est_start_at: '',
                est_due_at: ''
            });
        },
        
        removeReservationItem(index) {
            this.reservationForm.rd_list.splice(index, 1);
        },
        
        async handleCreateReservation() {
            try {
                this.loading = true;
                // 轉換時間格式
                const rd_list = this.reservationForm.rd_list.map(rd => ({
                    i_id: parseInt(rd.i_id),
                    p_id: parseInt(rd.p_id),
                    est_start_at: new Date(rd.est_start_at).toISOString(),
                    est_due_at: new Date(rd.est_due_at).toISOString()
                }));
                
                await api.createReservation(rd_list);
                this.showReservationModal = false;
                this.showSuccess('預約成功！');
                await this.loadMyReservations();
            } catch (error) {
                this.showError(error.response?.data?.error || '預約失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async reportItem(i_id) {
            const comment = prompt('請輸入檢舉原因：');
            if (!comment) return;
            
            try {
                this.loading = true;
                await api.reportItem(i_id, comment);
                this.showSuccess('檢舉已提交');
            } catch (error) {
                this.showError(error.response?.data?.error || '檢舉失敗');
            } finally {
                this.loading = false;
            }
        },
        
        // 個人紀錄 (Member)
        async loadMyReservations() {
            try {
                this.loading = true;
                const result = await api.getMyReservations();
                this.myReservations = result.reservations || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async viewReservationDetail(r_id) {
            try {
                const result = await api.getReservationDetail(r_id);
                let detailText = '預約詳情：\n';
                result.reservation_details.forEach((rd, index) => {
                    detailText += `\n物品 ${index + 1}:\n`;
                    detailText += `物品名稱: ${rd.i_name}\n`;
                    detailText += `取貨地點: ${rd.p_name}\n`;
                    detailText += `開始時間: ${this.formatDate(rd.est_start_at)}\n`;
                    detailText += `歸還時間: ${this.formatDate(rd.est_due_at)}\n`;
                });
                alert(detailText);
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            }
        },
        
        async cancelReservation(r_id) {
            if (!confirm('確定要取消這個預約嗎？')) return;
            
            try {
                this.loading = true;
                await api.deleteReservation(r_id);
                this.showSuccess('預約已取消');
                await this.loadMyReservations();
            } catch (error) {
                this.showError(error.response?.data?.error || '取消失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async loadReviewableItems() {
            try {
                this.loading = true;
                const result = await api.getReviewableItems();
                this.reviewableItems = result.reviewable_items || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        showReviewModal(item) {
            this.reviewForm.l_id = item.l_id;
            this.reviewForm.score = 5;
            this.reviewForm.comment = '';
            this.showReviewModalFlag = true;
        },
        
        async handleReview() {
            try {
                this.loading = true;
                await api.reviewItem(
                    this.reviewForm.l_id,
                    parseInt(this.reviewForm.score),
                    this.reviewForm.comment
                );
                this.showReviewModalFlag = false;
                this.showSuccess('評論已提交');
                await this.loadReviewableItems();
            } catch (error) {
                this.showError(error.response?.data?.error || '評論失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async loadContributions() {
            try {
                this.loading = true;
                const result = await api.getContributions();
                this.contributions = result.contributions || [];
                this.bans = result.bans || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        // 員工功能
        async loadVerifications() {
            try {
                this.loading = true;
                const result = await api.getNotDealVerification();
                this.verifications = result.verifications || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async concludeVerification(iv_id, conclusion) {
            try {
                this.loading = true;
                await api.concludeVerification(iv_id, conclusion);
                this.showSuccess(`驗證已${conclusion === 'Pass' ? '通過' : '不通過'}`);
                await this.loadVerifications();
            } catch (error) {
                this.showError(error.response?.data?.error || '處理失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async loadReports() {
            try {
                this.loading = true;
                const result = await api.getNotDealReports();
                this.reports = result.reports || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        async concludeReport(re_id, conclusion) {
            if (!confirm(`確定要${conclusion === 'Withdraw' ? '撤回' : conclusion === 'Ban Category' ? '封鎖類別' : '下架'}這個檢舉嗎？`)) return;
            
            try {
                this.loading = true;
                await api.concludeReport(re_id, conclusion);
                this.showSuccess('檢舉已處理');
                await this.loadReports();
            } catch (error) {
                this.showError(error.response?.data?.error || '處理失敗');
            } finally {
                this.loading = false;
            }
        },
        
        // 工具方法
        getStatusBadgeClass(status) {
            const classes = {
                'Not verified': 'bg-secondary',
                'Reservable': 'bg-success',
                'Not reservable': 'bg-danger',
                'Borrowed': 'bg-warning'
            };
            return classes[status] || 'bg-secondary';
        },
        
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('zh-TW');
        },
        
        showError(message) {
            this.errorMessage = message;
            setTimeout(() => {
                this.errorMessage = '';
            }, 5000);
        },
        
        showSuccess(message) {
            this.successMessage = message;
            setTimeout(() => {
                this.successMessage = '';
            }, 3000);
        }
    },
    
    watch: {
        currentView(newView) {
            if (!this.isLoggedIn) return;
            
            // 根據視圖載入對應資料
            if (newView === 'myItems') {
                this.loadMyItems();
            } else if (newView === 'browseItems') {
                // 載入類別列表（這裡需要後端提供 API，暫時跳過）
                // this.loadCategories();
            } else if (newView === 'myRecords') {
                if (this.recordsTab === 'reservations') {
                    this.loadMyReservations();
                } else if (this.recordsTab === 'reviews') {
                    this.loadReviewableItems();
                } else if (this.recordsTab === 'contributions') {
                    this.loadContributions();
                }
            } else if (newView === 'staffVerification') {
                this.loadVerifications();
            } else if (newView === 'staffReports') {
                this.loadReports();
            }
        },
        
        recordsTab(newTab) {
            if (newTab === 'reservations') {
                this.loadMyReservations();
            } else if (newTab === 'reviews') {
                this.loadReviewableItems();
            } else if (newTab === 'contributions') {
                this.loadContributions();
            }
        }
    }
}).mount('#app');

