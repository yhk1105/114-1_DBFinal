// MongoDB 索引建立腳本
// 在 MongoDB Compass 的 Shell 中執行

// 重要：先切換到正確的資料庫
use our_things_funnel_tracking;

// 1. session_id (唯一索引)
db.user_sessions.createIndex({ "session_id": 1 }, { unique: true });
print("✅ 索引 1: session_id (unique) 建立完成");

// 2. user_token
db.user_sessions.createIndex({ "user_token": 1 });
print("✅ 索引 2: user_token 建立完成");

// 3. m_id
db.user_sessions.createIndex({ "m_id": 1 });
print("✅ 索引 3: m_id 建立完成");

// 4. created_at
db.user_sessions.createIndex({ "created_at": 1 });
print("✅ 索引 4: created_at 建立完成");

// 5. funnel_stage
db.user_sessions.createIndex({ "funnel_stage": 1 });
print("✅ 索引 5: funnel_stage 建立完成");

// 6. events.timestamp (巢狀欄位)
db.user_sessions.createIndex({ "events.timestamp": 1 });
print("✅ 索引 6: events.timestamp 建立完成");

print("\n🎉 所有索引建立完成！");

// 顯示所有索引
print("\n現有索引列表:");
db.user_sessions.getIndexes().forEach(function(index) {
    print("  - " + index.name + ": " + JSON.stringify(index.key));
});

