-- MEMBER
SELECT setval(
  'our_things.member_m_id_seq',
  COALESCE((SELECT MAX(m_id) FROM our_things.member), 1)
);

-- CATEGORY
SELECT setval(
  'our_things.category_c_id_seq',
  COALESCE((SELECT MAX(c_id) FROM our_things.category), 1)
);
-- STAFF
SELECT setval(
  'our_things.staff_s_id_seq',
  COALESCE((SELECT MAX(s_id) FROM our_things.staff), 1)
);

-- PICK_UP_PLACE
SELECT setval(
  'our_things.pick_up_place_p_id_seq',
  COALESCE((SELECT MAX(p_id) FROM our_things.pick_up_place), 1)
);
-- ITEM
SELECT setval(
  'our_things.item_i_id_seq',
  COALESCE((SELECT MAX(i_id) FROM our_things.item), 1)
);

-- ITEM_VERIFICATION
SELECT setval(
  'our_things.item_verification_iv_id_seq',
  COALESCE((SELECT MAX(iv_id) FROM our_things.item_verification), 1)
);

-- RESERVATION
SELECT setval(
  'our_things.reservation_r_id_seq',
  COALESCE((SELECT MAX(r_id) FROM our_things.reservation), 1)
);

-- RESERVATION_DETAIL
SELECT setval(
  'our_things.reservation_detail_rd_id_seq',
  COALESCE((SELECT MAX(rd_id) FROM our_things.reservation_detail), 1)
);

--report
SELECT setval(
  'our_things.report_re_id_seq',
  COALESCE((SELECT MAX(re_id) FROM our_things.report), 1)
);
--loan
SELECT setval(
  'our_things.loan_l_id_seq',
  COALESCE((SELECT MAX(l_id) FROM our_things.loan), 1)
);
--review
SELECT setval(
  'our_things.review_review_id_seq',
  COALESCE((SELECT MAX(review_id) FROM our_things.review), 1)
);