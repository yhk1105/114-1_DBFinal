CREATE INDEX idx_item_c_id ON item(c_id);

-- reservation 表
CREATE INDEX idx_reservation_m_id ON reservation(m_id);

-- reservation_detail 表
CREATE INDEX idx_reservation_detail_r_id ON reservation_detail(r_id);
CREATE INDEX idx_reservation_detail_i_id ON reservation_detail(i_id);
CREATE INDEX idx_reservation_detail_time_range ON reservation_detail(i_id, est_start_at, est_due_at);

-- contribution 表
CREATE INDEX idx_contribution_m_id_i_id ON contribution(m_id, i_id);
CREATE INDEX idx_category_parent_c_id ON category(parent_c_id);

-- review 表
CREATE INDEX idx_review_l_id ON review(l_id);
CREATE INDEX idx_review_reviewee_id ON review(reviewee_id);

-- report 表
CREATE INDEX idx_report_s_id_conclusion ON report(s_id, r_conclusion);

-- category_ban 表
CREATE INDEX idx_category_ban_m_id ON category_ban(m_id) WHERE is_deleted = false;

