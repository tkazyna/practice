-- PROCEDURE: ADD PHONE

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- ищем контакт по first_name
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Контакт "%" не найден', p_contact_name;
    END IF;

    -- проверка типа телефона
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Тип телефона должен быть: home, work или mobile';
    END IF;

    -- добавляем номер
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


-- PROCEDURE: MOVE TO GROUP

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id   INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- ищем группу
    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    -- если группы нет → создаём
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name)
        VALUES (p_group_name)
        RETURNING id INTO v_group_id;
    END IF;

    -- ищем контакт
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Контакт "%" не найден', p_contact_name;
    END IF;

    -- обновляем группу
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$;


-- FUNCTION: SEARCH CONTACTS

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phone      VARCHAR,
    phone_type VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name,
        ph.phone,
        ph.type
    FROM contacts c
    LEFT JOIN groups g
        ON c.group_id = g.id
    LEFT JOIN phones ph
        ON ph.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR c.last_name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR ph.phone ILIKE '%' || p_query || '%'
    ORDER BY c.first_name;
END;
$$;