-- MEMBER
SELECT setval(
  'member_m_id_seq',
  COALESCE((SELECT MAX(m_id) FROM member), 1)
);

-- CATEGORY
SELECT setval(
  'category_c_id_seq',
  COALESCE((SELECT MAX(c_id) FROM category), 1)
);
-- STAFF
SELECT setval(
  'staff_s_id_seq',
  COALESCE((SELECT MAX(s_id) FROM staff), 1)
);

-- PICK_UP_PLACE
SELECT setval(
  'pick_up_place_p_id_seq',
  COALESCE((SELECT MAX(p_id) FROM pick_up_place), 1)
);
-- ITEM
SELECT setval(
  'item_i_id_seq',
  COALESCE((SELECT MAX(i_id) FROM item), 1)
);

-- ITEM_VERIFICATION
SELECT setval(
  'item_verification_iv_id_seq',
  COALESCE((SELECT MAX(iv_id) FROM item_verification), 1)
);

-- RESERVATION
SELECT setval(
  'reservation_r_id_seq',
  COALESCE((SELECT MAX(r_id) FROM reservation), 1)
);

-- RESERVATION_DETAIL
SELECT setval(
  'reservation_detail_rd_id_seq',
  COALESCE((SELECT MAX(rd_id) FROM reservation_detail), 1)
);

--report
SELECT setval(
  'report_re_id_seq',
  COALESCE((SELECT MAX(re_id) FROM report), 1)
);
--loan
SELECT setval(
  'loan_l_id_seq',
  COALESCE((SELECT MAX(l_id) FROM loan), 1)
);
--review
SELECT setval(
  'review_review_id_seq',
  COALESCE((SELECT MAX(review_id) FROM review), 1)
);