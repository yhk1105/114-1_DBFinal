// API 基礎設定
const API_BASE_URL = 'http://localhost:8070';

// Session ID 管理
function getSessionId() {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
        // 生成新的 session_id
        sessionId = crypto.randomUUID();
        localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
}

// 取得請求 headers（包含 Session ID 和 Token）
function getHeaders(includeAuth = false) {
    const headers = {
        'X-Session-ID': getSessionId(),
        'Content-Type': 'application/json'
    };
    
    if (includeAuth) {
        const token = localStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.warn('Token not found in localStorage');
        }
    }
    
    return headers;
}

// API 服務類別
const api = {
    // 認證相關
    async login(email, password, login_as = 'member') {
        const response = await axios.post(`${API_BASE_URL}/login`, {
            email,
            password,
            login_as
        }, {
            headers: getHeaders()
        });
        return response.data;
    },

    async register(name, email, password) {
        const response = await axios.post(`${API_BASE_URL}/register`, {
            name,
            email,
            password
        }, {
            headers: getHeaders()
        });
        return response.data;
    },

    // 物品相關
    async getItemDetail(i_id) {
        const response = await axios.get(`${API_BASE_URL}/item/${i_id}`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getCategoryItems(c_id) {
        const response = await axios.get(`${API_BASE_URL}/item/category/${c_id}`, {
            headers: getHeaders()
        });
        return response.data;
    },

    async getItemBorrowedTime(i_id) {
        const response = await axios.get(`${API_BASE_URL}/item/${i_id}/borrowed_time`, {
            headers: getHeaders()
        });
        return response.data;
    },

    async uploadItem(data) {
        const response = await axios.post(`${API_BASE_URL}/item/upload`, data, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async updateItem(i_id, data) {
        const response = await axios.put(`${API_BASE_URL}/item/${i_id}`, data, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async reportItem(i_id, comment) {
        const response = await axios.post(`${API_BASE_URL}/item/${i_id}/report`, { comment }, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async verifyItem(i_id) {
        const response = await axios.post(`${API_BASE_URL}/item/${i_id}/verify`, {}, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    // 個人資料相關
    async getProfile() {
        const response = await axios.get(`${API_BASE_URL}/me/profile`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getMyItems() {
        const response = await axios.get(`${API_BASE_URL}/me/items`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getMyReservations() {
        const response = await axios.get(`${API_BASE_URL}/me/reservations`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getReservationDetail(r_id) {
        const response = await axios.get(`${API_BASE_URL}/me/reservation_detail/${r_id}`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getReviewableItems() {
        const response = await axios.get(`${API_BASE_URL}/me/reviewable_items`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async reviewItem(l_id, score, comment) {
        const response = await axios.post(`${API_BASE_URL}/me/review_item/${l_id}`, {
            score,
            comment
        }, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getContributions() {
        const response = await axios.get(`${API_BASE_URL}/me/contributions`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    // 物主相關
    async getFutureReservationDetails() {
        const response = await axios.get(`${API_BASE_URL}/owner/future_reservation_details`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async punchInLoan(l_id, event_type) {
        const response = await axios.post(`${API_BASE_URL}/owner/punch_in_loan/${l_id}`, {
            event_type
        }, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    // 預約相關
    async createReservation(rd_list) {
        const response = await axios.post(`${API_BASE_URL}/reservation/create`, {
            rd_list
        }, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async deleteReservation(r_id) {
        const response = await axios.delete(`${API_BASE_URL}/reservation/delete/${r_id}`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getPickupPlaces(i_id) {
        const response = await axios.get(`${API_BASE_URL}/reservation/${i_id}`, {
            headers: getHeaders()
        });
        return response.data;
    },

    async getAllPickupPlaces() {
        const response = await axios.get(`${API_BASE_URL}/pickup-places`, {
            headers: getHeaders()
        });
        return response.data;
    },

    async getSubcategories(c_id) {
        const response = await axios.get(`${API_BASE_URL}/item/category/${c_id}/subcategories`, {
            headers: getHeaders()
        });
        return response.data;
    },

    // 員工相關
    async getStaff() {
        const response = await axios.get(`${API_BASE_URL}/staff`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getNotDealReports() {
        const response = await axios.get(`${API_BASE_URL}/staff/report`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async concludeReport(re_id, r_conclusion) {
        const response = await axios.post(`${API_BASE_URL}/staff/report/${re_id}`, {
            r_conclusion
        }, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async getNotDealVerification() {
        const response = await axios.get(`${API_BASE_URL}/staff/verification`, {
            headers: getHeaders(true)
        });
        return response.data;
    },

    async concludeVerification(iv_id, v_conclusion) {
        const response = await axios.post(`${API_BASE_URL}/staff/verification/${iv_id}`, {
            v_conclusion
        }, {
            headers: getHeaders(true)
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
                p_id_list: []
            },
            editForm: {
                i_id: null,
                i_name: '',
                description: '',
                out_duration: '',
                c_id: '',
                p_id_list: []
            },
            // 類別選擇器狀態
            categorySelector: {
                displayText: '',
                selectedPath: [], // [{c_id, c_name}, ...]
                currentSubcategories: [],
                showDropdown: false,
                isUploadForm: true // true for upload, false for edit
            },
            // 瀏覽頁面類別選擇器狀態
            browseCategorySelector: {
                displayText: '',
                selectedPath: [], // [{c_id, c_name}, ...]
                currentSubcategories: [],
                showDropdown: false
            },
            // 取貨地點列表
            allPickupPlaces: [],
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
                
                // 檢查是否已登入
                const token = localStorage.getItem('token');
                if (!token) {
                    this.showError('請先登入');
                    return;
                }
                
                // 驗證必要欄位
                if (!this.uploadForm.i_name || !this.uploadForm.i_name.trim()) {
                    this.showError('請輸入物品名稱');
                    return;
                }
                
                if (!this.uploadForm.description || !this.uploadForm.description.trim()) {
                    this.showError('請輸入物品描述');
                    return;
                }
                
                if (!this.uploadForm.out_duration || parseInt(this.uploadForm.out_duration) <= 0) {
                    this.showError('請輸入有效的外借時長');
                    return;
                }
                
                // 取得最後選擇的類別 ID
                const finalCId = this.categorySelector.selectedPath.length > 0 
                    ? this.categorySelector.selectedPath[this.categorySelector.selectedPath.length - 1].c_id 
                    : null;
                
                if (!finalCId) {
                    this.showError('請選擇類別');
                    return;
                }
                
                if (!this.uploadForm.p_id_list || this.uploadForm.p_id_list.length === 0) {
                    this.showError('請至少選擇一個取貨地點');
                    return;
                }
                
                const data = {
                    i_name: this.uploadForm.i_name.trim(),
                    description: this.uploadForm.description.trim(),
                    out_duration: parseInt(this.uploadForm.out_duration),
                    c_id: finalCId,
                    p_id_list: this.uploadForm.p_id_list
                };
                
                console.log('上傳物品數據:', data);
                const result = await api.uploadItem(data);
                console.log('上傳成功:', result);
                
                this.showUploadModal = false;
                this.resetUploadForm();
                this.showSuccess('物品上傳成功！');
                await this.loadMyItems();
            } catch (error) {
                console.error('上傳失敗:', error);
                console.error('錯誤詳情:', {
                    message: error.message,
                    response: error.response?.data,
                    status: error.response?.status
                });
                const errorMessage = error.response?.data?.error || error.message || '上傳失敗';
                this.showError(errorMessage);
            } finally {
                this.loading = false;
            }
        },
        
        resetUploadForm() {
            this.uploadForm = { i_name: '', description: '', out_duration: '', c_id: '', p_id_list: [] };
            this.categorySelector = {
                displayText: '',
                selectedPath: [],
                currentSubcategories: [],
                showDropdown: false,
                isUploadForm: true
            };
        },
        
        async editItem(item) {
            this.editForm = {
                i_id: item.i_id,
                i_name: item.i_name,
                description: item.description,
                out_duration: item.out_duration,
                c_id: item.c_id,
                p_id_list: [] // 這裡應該從資料庫取得，暫時留空
            };
            // 初始化編輯表單的類別選擇器
            this.categorySelector.isUploadForm = false;
            this.categorySelector.selectedPath = [];
            this.categorySelector.displayText = '';
            this.categorySelector.currentSubcategories = [];
            this.categorySelector.showDropdown = false;
            // 載入根類別
            await this.loadSubcategories(0, false);
            this.showEditModal = true;
        },
        
        async handleUpdateItem() {
            try {
                this.loading = true;
                const data = {};
                if (this.editForm.i_name) data.i_name = this.editForm.i_name;
                if (this.editForm.description) data.description = this.editForm.description;
                if (this.editForm.out_duration) data.out_duration = parseInt(this.editForm.out_duration);
                
                // 如果有選擇新的類別，使用新類別
                if (this.categorySelector.selectedPath.length > 0) {
                    const finalCId = this.categorySelector.selectedPath[this.categorySelector.selectedPath.length - 1].c_id;
                    data.c_id = finalCId;
                } else if (this.editForm.c_id) {
                    data.c_id = parseInt(this.editForm.c_id);
                }
                
                if (this.editForm.p_id_list && this.editForm.p_id_list.length > 0) {
                    data.p_id_list = this.editForm.p_id_list;
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
            // 取得最後選擇的類別 ID
            const finalCId = this.browseCategorySelector.selectedPath.length > 0 
                ? this.browseCategorySelector.selectedPath[this.browseCategorySelector.selectedPath.length - 1].c_id 
                : null;
            
            if (!finalCId) {
                this.browseItems = [];
                return;
            }
            
            try {
                this.loading = true;
                const result = await api.getCategoryItems(finalCId);
                this.browseItems = result.items || [];
            } catch (error) {
                this.showError(error.response?.data?.error || '載入失敗');
            } finally {
                this.loading = false;
            }
        },
        
        // 瀏覽頁面類別選擇器相關方法
        async loadBrowseSubcategories(c_id) {
            try {
                const result = await api.getSubcategories(c_id);
                this.browseCategorySelector.currentSubcategories = result.subcategories || [];
                this.browseCategorySelector.showDropdown = true;
                
                console.log('載入瀏覽子類別成功:', {
                    c_id,
                    count: this.browseCategorySelector.currentSubcategories.length,
                    items: this.browseCategorySelector.currentSubcategories
                });
            } catch (error) {
                console.error('載入瀏覽子類別失敗:', error);
                this.showError(error.response?.data?.error || '載入子類別失敗');
                // 即使出錯也顯示下拉選單（如果已經有選擇）
                if (this.browseCategorySelector.selectedPath.length > 0) {
                    this.browseCategorySelector.showDropdown = true;
                }
            }
        },
        
        async onBrowseCategoryFieldClick(event) {
            // 阻止事件冒泡，避免關閉下拉選單
            if (event) {
                event.stopPropagation();
            }
            
            // 如果還沒有選擇任何類別，載入根類別
            if (this.browseCategorySelector.selectedPath.length === 0) {
                // 先顯示下拉選單（即使還在載入）
                this.browseCategorySelector.showDropdown = true;
                await this.loadBrowseSubcategories(0);
            } else {
                // 如果已經有選擇，顯示當前層級的子類別
                const lastSelected = this.browseCategorySelector.selectedPath[this.browseCategorySelector.selectedPath.length - 1];
                // 先顯示下拉選單（即使還在載入）
                this.browseCategorySelector.showDropdown = true;
                await this.loadBrowseSubcategories(lastSelected.c_id);
            }
        },
        
        async selectBrowseCategory(category) {
            // 將選中的類別加入路徑
            this.browseCategorySelector.selectedPath.push(category);
            
            // 更新顯示文字（用 \ 分隔）
            this.browseCategorySelector.displayText = this.browseCategorySelector.selectedPath
                .map(c => c.c_name)
                .join(' \\ ');
            
            // 載入下一層級的子類別
            await this.loadBrowseSubcategories(category.c_id);
            
            // 自動載入該類別的物品
            await this.loadCategoryItems();
        },
        
        finishBrowseCategorySelection() {
            // 使用者決定不再繼續選擇，關閉下拉選單
            this.browseCategorySelector.showDropdown = false;
            // 載入該類別的物品
            this.loadCategoryItems();
        },
        
        clearBrowseCategory() {
            // 清除選擇
            this.browseCategorySelector = {
                displayText: '',
                selectedPath: [],
                currentSubcategories: [],
                showDropdown: false
            };
            // 清空物品列表
            this.browseItems = [];
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
        },
        
        // 類別選擇器相關方法
        async loadSubcategories(c_id, isUploadForm = true) {
            try {
                const result = await api.getSubcategories(c_id);
                this.categorySelector.currentSubcategories = result.subcategories || [];
                this.categorySelector.showDropdown = true;
                this.categorySelector.isUploadForm = isUploadForm;
                
                console.log('載入子類別成功:', {
                    c_id,
                    count: this.categorySelector.currentSubcategories.length,
                    subcategories: this.categorySelector.currentSubcategories,
                    result: result
                });
            } catch (error) {
                console.error('載入子類別失敗:', error);
                console.error('錯誤詳情:', {
                    message: error.message,
                    response: error.response?.data,
                    status: error.response?.status
                });
                this.showError(error.response?.data?.error || error.message || '載入子類別失敗');
                // 即使出錯也顯示下拉選單（如果已經有選擇）
                if (this.categorySelector.selectedPath.length > 0) {
                    this.categorySelector.showDropdown = true;
                } else {
                    // 如果沒有選擇且出錯，關閉下拉選單
                    this.categorySelector.showDropdown = false;
                }
            }
        },
        
        async onCategoryFieldClick(isUploadForm = true, event) {
            // 阻止事件冒泡，避免關閉下拉選單
            if (event) {
                event.stopPropagation();
            }
            
            this.categorySelector.isUploadForm = isUploadForm;
            
            // 如果還沒有選擇任何類別，載入根類別
            if (this.categorySelector.selectedPath.length === 0) {
                // 先顯示下拉選單（即使還在載入）
                this.categorySelector.showDropdown = true;
                await this.loadSubcategories(0, isUploadForm);
            } else {
                // 如果已經有選擇，顯示當前層級的子類別
                const lastSelected = this.categorySelector.selectedPath[this.categorySelector.selectedPath.length - 1];
                // 先顯示下拉選單（即使還在載入）
                this.categorySelector.showDropdown = true;
                await this.loadSubcategories(lastSelected.c_id, isUploadForm);
            }
        },
        
        async selectCategory(category) {
            // 將選中的類別加入路徑
            this.categorySelector.selectedPath.push(category);
            
            // 更新顯示文字（用 \ 分隔）
            this.categorySelector.displayText = this.categorySelector.selectedPath
                .map(c => c.c_name)
                .join(' \\ ');
            
            // 更新表單的 c_id（使用最後選擇的類別）
            if (this.categorySelector.isUploadForm) {
                this.uploadForm.c_id = category.c_id;
            } else {
                this.editForm.c_id = category.c_id;
            }
            
            // 載入下一層級的子類別
            await this.loadSubcategories(category.c_id, this.categorySelector.isUploadForm);
            
            // 保持下拉選單打開，讓使用者可以繼續選擇或完成
        },
        
        finishCategorySelection() {
            // 使用者決定不再繼續選擇，關閉下拉選單
            this.categorySelector.showDropdown = false;
            // 最終的 c_id 已經在 selectedPath 的最後一個元素中
        },
        
        resetCategorySelector() {
            this.categorySelector = {
                displayText: '',
                selectedPath: [],
                currentSubcategories: [],
                showDropdown: false,
                isUploadForm: true
            };
        },
        
        // 取貨地點相關方法
        async loadAllPickupPlaces() {
            try {
                const result = await api.getAllPickupPlaces();
                this.allPickupPlaces = result.pickup_places || [];
            } catch (error) {
                // 如果 API 不存在，顯示錯誤訊息
                this.showError('無法載入取貨地點列表，請確認後端 API 已實作');
                console.error('Error loading pickup places:', error);
            }
        },
        
        togglePickupPlace(p_id) {
            const index = this.getCurrentForm().p_id_list.indexOf(p_id);
            if (index > -1) {
                this.getCurrentForm().p_id_list.splice(index, 1);
            } else {
                this.getCurrentForm().p_id_list.push(p_id);
            }
        },
        
        getCurrentForm() {
            return this.categorySelector.isUploadForm ? this.uploadForm : this.editForm;
        },
        
        isPickupPlaceSelected(p_id) {
            return this.getCurrentForm().p_id_list.includes(p_id);
        }
    },
    
    watch: {
        currentView(newView) {
            if (!this.isLoggedIn) return;
            
            // 根據視圖載入對應資料
            if (newView === 'myItems') {
                this.loadMyItems();
            } else if (newView === 'browseItems') {
                // 初始化瀏覽頁面的類別選擇器
                this.browseCategorySelector = {
                    displayText: '',
                    selectedPath: [],
                    currentSubcategories: [],
                    showDropdown: false
                };
                this.browseItems = [];
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
        },
        
        showUploadModal(newVal) {
            if (newVal) {
                // Modal 打開時載入取貨地點列表和初始化類別選擇器
                this.loadAllPickupPlaces();
                this.resetCategorySelector();
                this.categorySelector.isUploadForm = true;
                this.categorySelector.showDropdown = false; // 初始狀態不顯示，等點擊時再顯示
            } else {
                // Modal 關閉時重置
                this.categorySelector.showDropdown = false;
            }
        },
        
        showEditModal(newVal) {
            if (newVal) {
                // Modal 打開時載入取貨地點列表和初始化類別選擇器
                this.loadAllPickupPlaces();
                this.categorySelector.isUploadForm = false;
                this.categorySelector.showDropdown = false; // 初始狀態不顯示，等點擊時再顯示
            } else {
                // Modal 關閉時重置
                this.categorySelector.showDropdown = false;
            }
        }
    }
}).mount('#app');

