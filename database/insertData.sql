-- SELECT current_database();

INSERT INTO member (m_id, m_name, m_mail, m_password, is_active)
VALUES
(1, 'elsa.chou', 'elsa.chou0614@ntu.edu.tw', 'pbkdf2:sha256:260000$6chQ812RxzuQDDxt$b482eb579f4f0cd9d74d63a02e36d27250461211f619bd618b75c5cb03b27805', TRUE),
(2, 'David Lin', 'david.1998@ntu.edu.tw',  'pbkdf2:sha256:260000$lz8nopbyjbg0PZnx$5073162bb4e7acb956cc28de06c8fff5498a182a2af7b0b98cc1e51f6092f8b6', TRUE),
(3, 'annwu', 'ann0302@ntu.edu.tw',  'pbkdf2:sha256:260000$GgSPheLZNjdG3ZVI$45d561722a918f01770b1ad9f7981437b0694af7aceb965da38d037f14b1793c', TRUE),
(4, 'peter_1120', 'peter_1120@ntu.edu.tw', 'scrypt:32768:8:1$HWjipkLtMgpBzaGV$cde5f028b795cac903a473956013c40187ff3d74eb528836618b44802a9873f35e27d84c9e54924e7e3c30c77552d9ee2ed03c4ef0401f87f112458c75fe4003', FALSE),
(5, 'lucywang0515', 'lucy0515@ntu.edu.tw', 'scrypt:32768:8:1$m1uvOWd8DrPn3XNE$01ccffe3ecbe321edce0ea2c09e16e1e0347f0db362eed21813fd70ff9b3fbed3a32940512b71dba89ad50d4402901cd5a713ee98b2f460923a0166a6f6052d0', TRUE),
(6, 'kevin8899', 'kevin8899@ntu.edu.tw', 'scrypt:32768:8:1$qqBhtv9tfsjHP2YQ$9c44eda39fbb52c49526d2287007f86c9537c73d9f1aadbbc5b45f8036f531e300239679f07fd9e5e586f69f0c7a393f2e31aa2e59ea2dc5b2d5a3c7fe710547', FALSE),
(7, 'tina0724', 'tina0724@ntu.edu.tw', 'scrypt:32768:8:1$pX3Qcdkzmxum9DNv$b02f6ccd76fadf55aea70493d0f9abedffd44e858ef250121303fa314adb6c60f158f49c192ec35b1ddf92a46d58c03e7052611cc3df34a44942fa0126d7a491', TRUE),
(8, 'jason.y', 'jason.work2020@ntu.edu.tw', 'scrypt:32768:8:1$L0Jpv1AQUGKpTYIZ$a489e9b0628f253fa8f00b0ffaa090b3ebbe0861a790e602bf34f44f6a311ccb72a3abc7cfd55f17a9ee41323f96256df0a345be45733a2ece3d4805f45015b8', TRUE),
(9, 'amy1010', 'amy1010@ntu.edu.tw', 'scrypt:32768:8:1$t4RaWXrm50qb7IVM$7d95d2d824bb8a7e39fbbd304cc5ff5f965391dede158dfe0014816b9070b9c36ef94bd697d9e19318656a1aac77716a9553f19c088148f7934e9b2eeee21eae', FALSE),
(10, 'brian.T.10', 'brian1017@ntu.edu.tw', 'scrypt:32768:8:1$YXfSRBVcODv0ZK7E$ea2918b0eccc62d587e25926a34570c6c093a03866f328f45d98004a4e3d8a9928942f8cb8b073682365f3e66a59bb515072d958067319d1eb401059c902b851', TRUE);

INSERT INTO category (c_id, c_name, parent_c_id) VALUES
-- 母類別 (1–10)
(1, '家電', NULL),
(2, '電腦與周邊', NULL),
(3, '文具用品', NULL),
(4, '運動健身', NULL),
(5, '戶外露營', NULL),
(6, '生活雜貨', NULL),
(7, '廚房用品', NULL),
(8, '個人配件', NULL),
(9, '服飾', NULL),
(10, '書籍', NULL),

-- 家電子類別
(11, '電風扇', 1),
(12, '電暖器', 1),
(13, '吸塵器', 1),
(14, '廚房家電', 1),

-- 電腦與周邊子類別
(15, '滑鼠', 2),
(16, '鍵盤', 2),
(17, 'HDMI 線', 2),
(18, '行動電源', 2),
(19, '螢幕支架', 2),

-- 文具用品子類別
(20, '螢光筆', 3),
(21, '筆記本', 3),
(22, '資料夾', 3),

-- 運動健身子類別
(23, '瑜珈墊', 4),
(24, '啞鈴', 4),
(25, '彈力繩', 4),
(26, '滾筒', 4),

-- 戶外露營子類別
(27, '露營椅', 5),
(28, '野餐墊', 5),
(29, '保溫壺', 5),
(30, 'LED 燈條', 5),

-- 生活雜貨子類別
(31, '掛勾', 6),
(32, '收納箱', 6),
(33, '裝飾品', 6),

-- 廚房用品子類別
(34, '平底鍋', 7),
(35, '砧板', 7),
(36, '攪拌碗', 7),
(37, '量杯', 7),

-- 個人配件子類別
(38, '雨傘', 8),
(39, '手套', 8),

-- 服飾子類別
(40, '短袖', 9),
(41, '長袖', 9),
(42, '連帽外套', 9),
(43, '牛仔褲', 9),

-- 書籍子類別
(44, '文學小說', 10),
(45, '社會科學', 10),
(46, '商業管理', 10),
(47, '心理學', 10),
(48, '統計學', 10);

-- item (out_duration 以秒為單位儲存)
INSERT INTO item (i_id, i_name, status, description, out_duration, m_id, c_id) VALUES
(7, '文學史（指定閱讀）', 'Reservable', '文學史通識用書，適合大一人文課程閱讀', 604800, 10, 10),
(14, '黑短袖', 'Not reservable', '出遊紀念品，清洗過狀況良好', 432000, 10, 40),
(1, '剪刀', 'Reservable', '文具剪刀，可剪紙、膠帶，適合手作使用', 172800, 1, 3),
(9, '啞鈴', 'Reservable', '1.5 公斤啞鈴一對，適合居家訓練', 259200, 5, 24),
(3, '直板夾', 'Reservable', '頭髮造型用直板夾，加熱迅速，建議小心使用', 172800, 2, 1),
(8, '彈力繩', 'Borrowed', '健身用阻力帶，中強度，適合暖身訓練', 172800, 8, 25),
(4, '水彩筆', 'Reservable', '一組 12 色水彩筆，適合手作剪貼或手帳使用', 259200, 3, 3),
(11, '捲尺', 'Reservable', '150 公分布捲尺，適合縫紉與量尺寸使用', 86400, 7, 3),
(17, '聖誕裝飾', 'Not verified', '小型聖誕樹與吊飾組合，適合活動派對聖誕佈置', 432000, 5, 33),
(15, '奶泡機', 'Reservable', '手持奶泡機，可打咖啡奶泡', 172800, 8, 14),
(5, '野餐墊', 'Reservable', '防水野餐墊，適合大安森林公園使用（4人）', 172800, 5, 28),
(13, '狗牌(共10個)', 'Reservable', '辦活動用', 86400, 10, 3),
(2, '摺疊桌', 'Reservable', '耐熱玻璃保鮮盒 800ml，可微波可烤箱', 259200, 2, 5),
(6, '書－晶片戰爭', 'Reservable', '《晶片戰爭》硬皮書，九成新，適合通識閱讀', 864000, 5, 46),
(18, '小電風扇', 'Reservable', 'USB 充電式小風扇，可三段風量調整', 172800, 10, 11),
(10, '瑜珈磚', 'Reservable', '泡棉瑜珈磚，適合瑜珈初學者使用', 259200, 6, 4),
(12, '膠帶', 'Reservable', '透明膠帶一卷，適合打包或文具用途', 86400, 10, 3),
(16, '鬆餅機', 'Reservable', '家用鬆餅機，可製作 2 份鬆餅，附食譜', 432000, 5, 14),
(19, '乾燥花', 'Reservable', '拍照擺飾', 432000, 7, 33),
(20, '生日氣球', 'Reservable', '生日派對布置', 259200, 8, 33),
(21, '電鑽', 'Not verified', '手動 DIY 裝置、組裝家具也可用', 432000, 8, 6),
(22, '打蛋器', 'Reservable', '最近比較少用的打蛋器', 432000, 6, 7),
(23, '隔熱手套', 'Not verified', '烤東西可以用', 172800, 6, 7),
(24, '果醬', 'Not reservable', '拍照擺飾', 432000, 7, 7),
(25, '螺絲起子', 'Reservable', '適合臨時要修理東西', 432000, 1, 6),
(26, '田園風桌巾', 'Reservable', '適合野餐、拍食物照', 172800, 2, 33),
(27, '餅乾模具', 'Reservable', '有動物系列和萬聖節系列~', 172800, 3, 7);

INSERT INTO staff (s_id, s_name, s_mail, s_password, role, is_deleted)
VALUES
(1, 'cyt', 'b11702080@ntu.edu.tw', 'scrypt:32768:8:1$Cc0lVpv6Hri8rQCR$1a71879ef4d3f964abb3dc7579a5f506d4779bd52be7686a6284307edf436794f5e6f83a3e4790569713824850f1886f8cd0662ff62ce84a73b313f411020dec', 'Manager', FALSE),
(2, 'yhk', 'b11611047@ntu.edu.tw', 'scrypt:32768:8:1$Iw9R5DhG3p2b7l9i$b6f7fb9f4c4abce51ce0fc84163c27791b79b13743968da1961091ba9b23a6fb0a1e78e0436bef908e666829637be74aee822df85595aa6e71fdc540a0fcd7c6', 'Employee', FALSE),
(3, 'hcw', 'b11702044@ntu.edu.tw', 'scrypt:32768:8:1$X8wDefe3TNADtWNm$5960b378190c1ab11aaf0170fab199967fb48b7c49205a51c1e2830f2adcbefb38de7d0eddf17459df298bf3758a2f89a297363032fa57dff7124078e0bfecd0', 'Employee', FALSE);


INSERT INTO item_verification (iv_id, v_conclusion, create_at, i_id, s_id) VALUES
(1,  'Pending', '2025-11-10 14:22', 1, 1),
(2,  'Pending', '2025-11-10 20:41', 2, 2),
(3,  'Pending', '2025-11-11 16:10', 3, 2),
(4,  'Pending', '2025-11-12 11:48', 4, 3),
(5,  'Pass',    '2025-11-13 09:18', 1, 1),
(6,  'Pending', '2025-11-13 09:32', 5, 2),
(7,  'Pass',    '2025-11-13 10:56', 3, 2),
(8,  'Pass',    '2025-11-13 14:32', 2, 2), 
(9,  'Pass',    '2025-11-13 15:40', 4, 3),
(10, 'Pending', '2025-11-13 18:25', 6, 1),
(11, 'Pass',    '2025-11-14 10:05', 5, 2),
(12, 'Pending', '2025-11-14 13:55', 7, 1),
(13, 'Pass',    '2025-11-14 15:10', 6, 1),
(14, 'Pending', '2025-11-14 20:01', 8, 1),
(15, 'Pass',    '2025-11-15 10:28', 7, 1),
(16, 'Pending', '2025-11-15 10:44', 8, 2),
(17, 'Pending', '2025-11-16 21:18', 9, 3),
(18, 'Pass',    '2025-11-17 11:40', 8, 2),
(19, 'Pending', '2025-11-17 14:09', 10, 1),
(20, 'Pass',    '2025-11-18 09:05', 10, 1),
(21, 'Pending', '2025-11-19 10:45', 11, 3),
(22, 'Pending', '2025-11-19 18:32', 13, 3),
(23, 'Pass',    '2025-11-21 09:12', 11, 3),
(24, 'Pending', '2025-11-21 10:50', 14, 2),
(25, 'Pass',    '2025-11-21 11:22', 13, 3),
(26, 'Pending', '2025-11-21 20:44', 12, 3),
(27, 'Fail',    '2025-11-22 09:12', 12, 3),
(28, 'Pending', '2025-11-22 09:35', 15, 1),
(29, 'Pass',    '2025-11-22 10:18', 14, 2),
(30, 'Pending', '2025-11-22 18:55', 12, 3),
(31, 'Pass',    '2025-11-23 08:42', 12, 3),
(32, 'Pass',    '2025-11-23 14:55', 15, 1),
(33, 'Pending', '2025-11-23 16:48', 16, 3),
(34, 'Pending', '2025-11-24 11:09', 17, 2),
(35, 'Pass',    '2025-11-24 15:20', 16, 3),
(36, 'Pending', '2025-11-25 13:58', 18, 2),
(37, 'Pass',    '2025-11-28 09:42', 18, 2),
(38, 'Pending', '2025-11-29 09:10', 19, 3),
(39, 'Pending', '2025-11-29 14:30', 20, 2),
(40, 'Pending', '2025-11-30 08:00', 21, 1),
(41, 'Pending', '2025-11-30 10:20', 22, 3),
(42, 'Pending', '2025-12-01 09:15', 23, 2),
(43, 'Pending', '2025-12-01 13:00', 24, 2),
(44, 'Pass',    '2025-12-01 15:40', 19, 3),
(45, 'Pending', '2025-12-02 09:10', 25, 1),
(46, 'Fail',    '2025-12-02 10:20', 24, 2),
(47, 'Pending', '2025-12-02 15:00', 26, 3),
(48, 'Pass',    '2025-12-02 18:10', 20, 2),
(49, 'Pending', '2025-12-03 09:00', 27, 1),
(50, 'Pass',    '2025-12-03 12:30', 22, 3),
(51, 'Pass',    '2025-12-03 15:50', 25, 1),
(52, 'Pass',    '2025-12-03 17:40', 26, 3),
(53, 'Pass',    '2025-12-03 18:20', 27, 1);

INSERT INTO pick_up_place (p_id, p_name, address, note, is_deleted) VALUES
(1, '活大一樓大廳', '羅斯福路四段一號 新生大樓', '近椰林大道，室內等候方便', FALSE),
(2, '心輔中心前廣場', '羅斯福路四段一號 心理系館', '陰涼處，好認', FALSE),
(3, '理圖入口前', '羅斯福路四段一號 理學院圖書館', '人潮多、安全明亮', FALSE),
(4, '社科院中庭', '羅斯福路四段一號 社會科學院', '近星巴克側門', FALSE),
(5, '管理學院一號館門口', '羅斯福路四段一號 管一', '上課動線常經過', FALSE),
(6, '新體育館入口', '羅斯福路四段一號 新體育館', '雨天不淋雨', FALSE),
(7, '醉月湖旁長廊', '羅斯福路四段一號 醉月湖區', '風景佳，有鴨子', FALSE),
(8, '資訊工程系館一樓', '羅斯福路四段一號 資工系館', '近側門電梯', FALSE),
(9, '地質系館一樓交誼廳', '羅斯福路四段一號 地質系館', '座位多，可短暫放物', FALSE),
(10, '研三一樓自習區外', '羅斯福路四段一號 研三宿舍', '學生宿舍區域', FALSE),
(11, '公館捷運站 2 號出口前', '臺北市中正區羅斯福路四段 222 號', '人潮多、好找', FALSE),
(12, '公館水源市場門口', '臺北市中正區羅斯福路四段 92 號', '靠近巷口，明顯', FALSE),
(13, '公館誠品前廣場', '臺北市中正區汀州路三段 131 號', '地標明顯', FALSE),
(14, '師大夜市入口（8巷口）', '臺北市大安區師大路 49 巷口', '近捷運台電站', FALSE),
(15, '118 巷全家外', '臺北市大安區新生南路三段 118 巷 5 號', '靠近宿舍，安全明亮', FALSE);

INSERT INTO item_pick (i_id, p_id, is_deleted) VALUES
(1, 2, FALSE),
(1, 5, FALSE),
(1, 9, FALSE),
(2, 1, FALSE),
(2, 4, FALSE),
(2, 7, FALSE),
(3, 3, FALSE),
(3, 8, FALSE),
(4, 2, FALSE),
(4, 6, FALSE),
(4, 11, FALSE),
(5, 1, FALSE),
(5, 10, FALSE),
(5, 12, FALSE),
(6, 4, FALSE),
(6, 9, FALSE),
(6, 13, FALSE),
(7, 2, FALSE),
(7, 5, FALSE),
(8, 3, FALSE),
(8, 7, FALSE),
(8, 14, FALSE),
(9, 6, FALSE),
(9, 12, FALSE),
(10, 1, FALSE),
(10, 8, FALSE),
(10, 15, FALSE),
(11, 4, FALSE),
(11, 9, FALSE),
(12, 5, FALSE),
(12, 10, FALSE),
(13, 3, FALSE),
(13, 11, FALSE),
(13, 14, FALSE),
(14, 2, FALSE),
(14, 6, FALSE),
(15, 7, FALSE),
(15, 13, FALSE),
(16, 8, FALSE),
(16, 10, FALSE),
(16, 15, FALSE),
(17, 5, FALSE),
(17, 9, FALSE),
(18, 1, FALSE),
(18, 12, FALSE),
(18, 14, FALSE),
(19, 3, FALSE),
(19, 6, FALSE),
(19, 10, FALSE),
(20, 2, FALSE),
(20, 5, FALSE),
(20, 11, FALSE),
(21, 1, FALSE),
(21, 4, FALSE),
(22, 7, FALSE),
(22, 9, FALSE),
(22, 13, FALSE),
(22, 15, FALSE),
(23, 3, FALSE),
(23, 8, FALSE),
(24, 2, FALSE),
(24, 5, FALSE),
(24, 12, FALSE),
(25, 6, FALSE),
(25, 10, FALSE),
(25, 14, FALSE),
(26, 1, FALSE),
(26, 9, FALSE),
(26, 11, FALSE),
(27, 4, FALSE),
(27, 7, FALSE),
(27, 15, FALSE);

INSERT INTO reservation (r_id, is_deleted, create_at, m_id) VALUES
(1, FALSE, '2025-11-28 11:00', 2),   -- i_id = 5
(2, FALSE, '2025-11-30 10:00', 5),   -- i_id = 10
(3, FALSE, '2025-11-30 13:00', 6),   -- i_id = 8
(4, TRUE, '2025-12-01 10:00', 7),   -- i_id = 1(取消預約)
(5, FALSE, '2025-12-03 16:00', 8),   -- i_id = 16
(6, FALSE, '2025-12-03 12:00', 10),  -- i_id = 6 & 15
(7, FALSE, '2025-12-04 16:00', 6), -- i_id = 27
(8, FALSE, '2025-12-05 21:00', 8);-- i_id = 26

INSERT INTO reservation_detail (rd_id, est_start_at, est_due_at, r_id, i_id, p_id) VALUES
(1, '2025-12-01 09:00', '2025-12-03 09:00', 1, 5, 10),   -- i_id=5
(2, '2025-12-02 10:00', '2025-12-04 10:00', 2, 10, 8),  -- i_id=10 
(3, '2025-12-03 08:00', '2025-12-05 08:00', 3, 8, 3),   -- i_id=8 
(4, '2025-12-03 12:00', '2025-12-05 10:00', 4, 1, 5),   -- i_id=1
(5, '2025-12-05 10:00', '2025-12-08 10:00', 5, 16, 15), -- i_id=16 
(6, '2025-12-06 09:00', '2025-12-08 09:00', 6, 6, 4),   -- i_id=6 
(7, '2025-12-06 14:00', '2025-12-08 14:00', 6, 15, 13), -- i_id=15
(8, '2025-12-07 10:00', '2025-12-09 10:00', 7, 27, 7),  -- i_id=27
(9, '2025-12-08 09:00', '2025-12-10 09:00', 8, 26, 1);  -- i_id=26 

INSERT INTO loan (l_id, rd_id, actual_start_at, actual_return_at, is_deleted) VALUES
-- rd_id = 1 逾期三天
(1, 1, '2025-12-01 09:00', '2025-12-06 09:00', FALSE),
-- rd_id = 2 如期提前一天歸還
(2, 2, '2025-12-02 10:00', '2025-12-03 10:00', FALSE),
-- rd_id = 3 同意展期 7 天，新的到期日 = 12/12 08:00
(3, 3, '2025-12-03 08:00', '2025-12-12 08:00', FALSE);

INSERT INTO loan_event (timestamp, event_type, l_id) VALUES
-- l_id = 1: 逾期三天
(1764579600, 'Handover', 1),
(1764752400, 'Mark_overdue', 1),
(1765011600, 'Return', 1),
-- l_id = 2: 如期提前一天歸還
(1764669600, 'Handover', 2),
(1764756000, 'Return', 2),
-- l_id = 3: 展期 7 天
(1764748800, 'Handover', 3),
(1764921600, 'Extend', 3),
(1765526400, 'Return', 3);

INSERT INTO review (review_id, score, comment, reviewer_id, reviewee_id, l_id, is_deleted) VALUES
(1, 2, '借用時間大幅超過預計，有點影響到自己的使用，希望下次能準時歸還。', 5, 2, 1, FALSE),
(2, 5, '物品狀況很好，使用起來很方便，謝謝出借！', 2, 5, 1, FALSE),
(3, 5, '借用人準時且溝通順暢，歸還時物品也保持得很乾淨！', 6, 5, 2, FALSE),
(4, 5, '物主回覆很快，取還都很順利，物品也完全符合需求。', 5, 6, 2, FALSE),
(5, 4, '借用人有提前告知需展期，溝通良好，歸還時物品狀況也不錯。', 8, 6, 3, FALSE),
(6, 5, '物品很好用，展期也獲得物主友善協助，謝謝！', 6, 8, 3, FALSE);

INSERT INTO report (re_id, comment, r_conclusion, create_at, conclude_at, m_id, i_id, s_id)
VALUES
(1,
 '描述與實物不符，照片與文字內容明顯不同',
 'Withdraw',
 '2025-11-15 14:20',
 '2025-11-16 10:00',
 1,
 2,
 3),
(2,
 '物品描述含有不當字眼並涉嫌散播仇恨',
 'Ban Category',
 '2025-11-29 09:40',
 '2025-11-30 15:30',
 4,
 14,
 2
);

INSERT INTO contribution (m_id, i_id, is_active) VALUES
(10, 7, TRUE),     -- 文學史 Reservable
(10, 14, FALSE),   -- 黑短袖 Not reservable
(1, 1, TRUE),      -- 剪刀 Reservable
(5, 9, TRUE),      -- 啞鈴 Reservable
(2, 3, TRUE),      -- 直板夾 Reservable
(8, 8, TRUE),     -- 彈力繩 Borrowed
(3, 4, TRUE),      -- 水彩筆 Reservable
(7, 11, TRUE),     -- 捲尺 Reservable
(5, 17, FALSE),    -- 聖誕裝飾 Not Verified
(8, 15, TRUE),     -- 奶泡機 Reservable
(5, 5, TRUE),      -- 野餐墊 Reservable
(10, 13, TRUE),    -- 狗牌 Reservable
(2, 2, TRUE),      -- 摺疊桌 Reservable
(5, 6, TRUE),      -- 晶片戰爭 Reservable
(10, 18, TRUE),    -- 小電風扇 Reservable
(6, 10, TRUE),     -- 瑜珈磚 Reservable
(10, 12, TRUE),    -- 膠帶 Reservable
(5, 16, TRUE),     -- 鬆餅機 Reservable
(7, 19, TRUE),     -- 乾燥花 Reservable
(8, 20, TRUE),     -- 生日氣球 Reservable
(8, 21, FALSE),    -- 電鑽 Not Verified
(6, 22, TRUE),     -- 打蛋器 Reservable
(6, 23, FALSE),    -- 隔熱手套 Not Verified
(7, 24, FALSE),    -- 果醬 Not Reservable
(1, 25, TRUE),     -- 螺絲起子 Reservable
(2, 26, TRUE),     -- 田園風桌巾 Reservable
(3, 27, TRUE);     -- 餅乾模具 Reservable

INSERT INTO category_ban (s_id, c_id, m_id, is_deleted, ban_at) VALUES
(2, 9, 10, FALSE, '2025-11-30 15:30');
