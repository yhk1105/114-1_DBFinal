CREATE TABLE member (
    m_id BIGSERIAL PRIMARY KEY,
    m_name VARCHAR(20) NOT NULL UNIQUE,
    m_mail VARCHAR(60) NOT NULL UNIQUE,
    m_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE category (
    c_id BIGSERIAL PRIMARY KEY,
    c_name VARCHAR(20) NOT NULL,
    parent_c_id BIGINT,
    CONSTRAINT fk_category_parent
        FOREIGN KEY (parent_c_id)
        REFERENCES category(c_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE staff (
    s_id BIGSERIAL PRIMARY KEY,
    s_name VARCHAR(20) NOT NULL,
    s_mail VARCHAR(60) NOT NULL UNIQUE,
    s_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('Employee', 'Manager')),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE pick_up_place (
    p_id BIGSERIAL PRIMARY KEY,
    p_name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL,
    note VARCHAR(200),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE item (
    i_id BIGSERIAL PRIMARY KEY,
    i_name VARCHAR(20) NOT NULL,
    status VARCHAR(15) NOT NULL 
        CHECK (status IN ('Borrowed','Reservable','Not reservable', 'Not verified')),
    description VARCHAR(200),
    out_duration INT NOT NULL,
    m_id BIGINT NOT NULL,
    c_id BIGINT NOT NULL,
    CONSTRAINT fk_item_member
        FOREIGN KEY (m_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,
    CONSTRAINT fk_item_category
        FOREIGN KEY (c_id)
        REFERENCES category(c_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE item_pick (
    i_id BIGINT NOT NULL,
    p_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (i_id, p_id),

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (p_id)
        REFERENCES pick_up_place(p_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE item_photo (
    seq_no INT NOT NULL,
    i_id BIGINT NOT NULL,
    file_path VARCHAR(100) NOT NULL, --不知道夠不夠長
    upload_at TIMESTAMP NOT NULL,
    PRIMARY KEY (seq_no, i_id),

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE item_verification (
    iv_id BIGSERIAL PRIMARY KEY,
    v_conclusion VARCHAR(10) CHECK(v_conclusion IN ('Pass','Fail','Pending')),
    create_at TIMESTAMP NOT NULL,
    i_id BIGINT NOT NULL,
    s_id BIGINT NOT NULL DEFAULT 0,

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (s_id)
        REFERENCES staff(s_id)
        ON DELETE SET DEFAULT
        ON UPDATE CASCADE
);

CREATE TABLE reservation (
    r_id BIGSERIAL PRIMARY KEY,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    create_at TIMESTAMP NOT NULL,
    m_id BIGINT NOT NULL,

    FOREIGN KEY (m_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);

CREATE TABLE reservation_detail (
    rd_id BIGSERIAL PRIMARY KEY,
    est_start_at TIMESTAMP NOT NULL,
    est_due_at TIMESTAMP NOT NULL,
    r_id BIGINT NOT NULL,
    i_id BIGINT NOT NULL,
    p_id BIGINT NOT NULL,

    FOREIGN KEY (r_id)
        REFERENCES reservation(r_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (p_id)
        REFERENCES pick_up_place(p_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);

CREATE TABLE contribution (
    m_id BIGINT NOT NULL,
    i_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (m_id, i_id),

    FOREIGN KEY (m_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);

CREATE TABLE category_ban (
    s_id BIGINT NOT NULL DEFAULT 0,
    c_id BIGINT NOT NULL,
    m_id BIGINT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    ban_at TIMESTAMP NOT NULL,
    PRIMARY KEY (s_id, c_id, m_id),

    FOREIGN KEY (s_id)
        REFERENCES staff(s_id)
        ON DELETE SET DEFAULT
        ON UPDATE CASCADE,

    FOREIGN KEY (c_id)
        REFERENCES category(c_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (m_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
);

CREATE TABLE report (
    re_id BIGSERIAL PRIMARY KEY,
    comment VARCHAR(200) NOT NULL,
    r_conclusion VARCHAR(10) CHECK(r_conclusion IN ('Withdraw','Ban Category','Delist','Pending')),
    create_at TIMESTAMP NOT NULL,
    conclude_at TIMESTAMP,
    m_id BIGINT NOT NULL,
    i_id BIGINT NOT NULL,
    s_id BIGINT NOT NULL ,

    FOREIGN KEY (m_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (i_id)
        REFERENCES item(i_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (s_id)
        REFERENCES staff(s_id)
        ON DELETE SET DEFAULT
        ON UPDATE CASCADE
);

CREATE TABLE loan (
    l_id BIGSERIAL PRIMARY KEY,
    rd_id BIGINT NOT NULL UNIQUE,
    actual_start_at TIMESTAMP,
    actual_return_at TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (rd_id)
        REFERENCES reservation_detail(rd_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE loan_event (
    timestamp BIGINT NOT NULL,
    event_type VARCHAR(10) NOT NULL 
        CHECK (event_type IN ('Handover','Extend','Mark_overdue','Return')),
    l_id BIGINT NOT NULL,
    PRIMARY KEY (timestamp, l_id),

    FOREIGN KEY (l_id)
        REFERENCES loan(l_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE review (
    review_id BIGSERIAL PRIMARY KEY,
    score INT NOT NULL CHECK(score BETWEEN 1 AND 5),
    comment VARCHAR(200) NOT NULL,
    reviewer_id BIGINT NOT NULL,
    reviewee_id BIGINT NOT NULL,
    l_id BIGINT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (reviewer_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (reviewee_id)
        REFERENCES member(m_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,

    FOREIGN KEY (l_id)
        REFERENCES loan(l_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uniq_review_per_loan_reviewer
    UNIQUE (reviewer_id, l_id)
);


