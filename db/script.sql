DROP TABLE public.schemes CASCADE;
DROP TABLE public.chats CASCADE;
DROP TABLE public.messages CASCADE;
DROP TABLE public.attachments CASCADE;
DROP TABLE public.messagesContent CASCADE;
DROP TABLE public.messagesContent_ai CASCADE;
DROP TABLE public.messagesContent_user CASCADE;

CREATE TABLE IF NOT EXISTS public.schemes(
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    title text NOT NULL,
    content text NOT NULL,
    attachmentUrl text NULL DEFAULT NULL,
    userId uuid NOT NULL,
    createdAt timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT schemes_pk PRIMARY KEY (id),
    CONSTRAINT chats_userId_fk FOREIGN KEY (userId)
        REFERENCES next_auth.users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.chats (
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    userId uuid NOT NULL,
    schemeId uuid NULL DEFAULT NULL,
    nameChat text NULL DEFAULT NULL,
    createdAt timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT chats_pk PRIMARY KEY (id),
    CONSTRAINT chats_userId_fk FOREIGN KEY (userId)
        REFERENCES next_auth.users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE,
    CONSTRAINT chats_schemeId_fk FOREIGN KEY (schemeId)
        REFERENCES public.schemes (id)
            ON UPDATE NO ACTION
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.messagesContent (
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    CONSTRAINT content_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.messagesContent_ai (
    contentAnalysis text NULL DEFAULT NULL,
    contentComment text NULL DEFAULT NULL,
    contentCode text NULL DEFAULT NULL,
    contentExecutableCode text NULL DEFAULT NULL
) INHERITS (public.messagesContent);

CREATE TABLE IF NOT EXISTS public.messagesContent_user (
    content text NULL DEFAULT NULL
) INHERITS (public.messagesContent);

CREATE TABLE IF NOT EXISTS public.messages (
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    chatId uuid,
    createdAt timestamp with time zone NOT NULL DEFAULT now(),
    role text NOT NULL,
    contentId uuid NULL DEFAULT NULL,
    CONSTRAINT messages_pk PRIMARY KEY (id),
    CONSTRAINT messages_chatId_fk FOREIGN KEY (chatId)
        REFERENCES public.chats (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE,
    CONSTRAINT messages_contentId_fk FOREIGN KEY (contentId)
        REFERENCES public.messagesContent (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS public.attachments (
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    messageId uuid,
    url text NOT NULL,
    filename text NOT NULL,
    createdAt timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT attachments_pk PRIMARY KEY (id),
    CONSTRAINT attachments_messageId FOREIGN KEY (messageId)
        REFERENCES public.messages (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION public.get_all_users(
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM next_auth.users;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'name', u.name,
                            'email', u.email,
                            'emailVerified', u."emailVerified",
                            'image', u.image
                        )
                    )
                    FROM next_auth.users u
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_user_by_id(
    p_id uuid
)
RETURNS json AS $$
BEGIN

    RETURN (
        SELECT
            json_build_object(
                'id', u.id,
                'name', u.name,
                'email', u.email,
                'email_verified', u."emailVerified",
                'image', u.image
            )
        FROM next_auth.users u
        WHERE u.id = p_id
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public.get_user_by_email(
    p_email text
)
RETURNS json AS $$
BEGIN

    RETURN (
        SELECT
            json_build_object(
                'id', u.id,
                'name', u.name,
                'email', u.email,
                'email_verified', u."emailVerified",
                'image', u.image
            )
        FROM next_auth.users u
        WHERE u.email = p_email
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_scheme_by_id(
    p_id uuid
)
RETURNS json AS $$
BEGIN

    RETURN (
        SELECT
            json_build_object(
                'id', u.id,
                'title', u.title,
                'content', u.content,
                'attachment_url', u.attachmentUrl,
                'created_at', u.createdAt
            )
        FROM public.schemes u
        WHERE u.id = p_id
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public.get_all_schemes(
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.schemes;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'title', u.title,
                            'content', u.content,
                            'attachment_url', u.attachmentUrl,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.schemes u
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_scheme(
    p_title TEXT,
    p_content TEXT,
    p_user_id UUID,
    p_attachment_url TEXT DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_scheme_id UUID;
    v_scheme_createdAt timestamp with time zone;
BEGIN
    -- Insertar los datos en la tabla schemes
    INSERT INTO public.schemes(
        title,
        content,
        userId,
        attachmentUrl
    )
    VALUES (
        p_title,
        p_content,
        p_user_id,
        p_attachment_url
    )
    RETURNING id, createdAt INTO v_scheme_id, v_scheme_createdAt;

    -- Retornar el ID generado como JSON
    RETURN json_build_object('id', v_scheme_id, 'created_at', v_scheme_createdAt);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.update_scheme(
    p_id uuid,
    p_title text DEFAULT NULL,
    p_content text DEFAULT NULL,
    p_attachment_url text DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    updated_id uuid;
BEGIN
    -- Update the scheme record
    UPDATE public.schemes
    SET
        title = COALESCE(p_title, title),
        content = COALESCE(p_content, content),
        attachmentUrl = COALESCE(p_attachment_url, attachmentUrl)
    WHERE id = p_id
    RETURNING id INTO updated_id;

    -- Check if any row was updated
    IF updated_id IS NULL THEN
        RAISE EXCEPTION 'Scheme with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', updated_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.delete_scheme(
    p_id uuid
)
RETURNS JSON AS $$
DECLARE
    deleted_id uuid;
BEGIN
    -- Delete the scheme record
    DELETE FROM public.schemes
    WHERE id = p_id
    RETURNING id INTO deleted_id;

    -- Check if any row was deleted
    IF deleted_id IS NULL THEN
        RAISE EXCEPTION 'Scheme with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', deleted_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_chats(
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.chats;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'user_id', u.userId,
                            'scheme_id', u.schemeId,
                            'name_chat', u.nameChat,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.chats u
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_chat_by_id(
    p_id uuid
)
RETURNS json AS $$
BEGIN

    RETURN (
        SELECT
            json_build_object(
                'id', u.id,
                'user_id', u.userId,
                'scheme_id', u.schemeId,
                'name_chat', u.nameChat,
                'created_at', u.createdAt
            )
        FROM public.chats u
        WHERE u.id = p_id
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_chat(
    p_user_id uuid,
    p_scheme_id uuid DEFAULT NULL,
    p_name_chat text DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_chat_id uuid;
    v_chat_createdAt timestamp with time zone;
BEGIN
    -- Insertar los datos en la tabla chats
    INSERT INTO public.chats(
        userId,
        schemeId,
        nameChat
    )
    VALUES (
        p_user_id,
        p_scheme_id,
        p_name_chat
    )
    RETURNING id, createdAt INTO v_chat_id, v_chat_createdAt;

    -- Retornar el ID generado como JSON
    RETURN json_build_object('id', v_chat_id, 'created_at', v_chat_createdAt);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.update_chat(
    p_id uuid,
    p_user_id uuid DEFAULT NULL,
    p_scheme_id uuid DEFAULT NULL,
    p_name_chat text DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    updated_id uuid;
BEGIN
    -- Update the chat record
    UPDATE public.chats
    SET
        userId = COALESCE(p_user_id, userId),
        schemeId = COALESCE(p_scheme_id, schemeId),
        nameChat = COALESCE(p_name_chat, nameChat)
    WHERE id = p_id
    RETURNING id INTO updated_id;

    -- Check if any row was updated
    IF updated_id IS NULL THEN
        RAISE EXCEPTION 'Chat with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', updated_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.delete_chat(
    p_id uuid
)
RETURNS JSON AS $$
DECLARE
    deleted_id uuid;
BEGIN
    -- Delete the chat record
    DELETE FROM public.chats
    WHERE id = p_id
    RETURNING id INTO deleted_id;

    -- Check if any row was deleted
    IF deleted_id IS NULL THEN
        RAISE EXCEPTION 'Chat with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', deleted_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_messages_with_content(
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.messages;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(message_data ORDER BY created_at) AS messages
                    FROM (
                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                    'content', c.content
                                           )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_user c ON u.contentId = c.id AND u.role = 'user'

                        UNION

                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                    'content_analysis', c.contentAnalysis,
                                    'content_comment', c.contentComment,
                                    'content_code', c.contentCode,
                                    'content_executable_code', c.contentExecutableCode
                                )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_ai c ON u.contentId = c.id AND u.role = 'ai'
                    ) subquery
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_message_by_id(
    p_id uuid
)
RETURNS json AS $$
DECLARE
    v_contentId uuid;
    v_role text;
    v_chatId uuid;
    v_createdAt timestamp with time zone;
    v_result json;
BEGIN

    SELECT contentId, role, chatId, createdAt INTO v_contentId, v_role, v_chatId, v_createdAt FROM public.messages WHERE id = p_id;

    -- Verificar si el mensaje existe
    IF v_contentId IS NULL THEN
        RAISE EXCEPTION 'Message with ID % not found', p_id;
    END IF;

    IF v_role = 'ai' THEN
        SELECT
            json_build_object(
                'id', p_id,
                'chat_id', v_chatId,
                'created_at', v_createdAt,
                'role', v_role,
                'content_analysis', c.contentAnalysis,
                'content_comment', c.contentComment,
                'content_code', c.contentCode,
                'content_executable_code', c.contentExecutableCode
            )
        INTO v_result
        FROM public.messagesContent_ai c
        WHERE c.id = v_contentId
        LIMIT 1;
    ELSE
        SELECT
            json_build_object(
                'id', p_id,
                'chat_id', v_chatId,
                'created_at', v_createdAt,
                'role', v_role,
                'content', c.content
            )
        INTO v_result
        FROM public.messagesContent_user c
        WHERE c.id = v_contentId;
    END IF;

    -- Verificar si el mensaje fue encontrado
    IF v_result IS NULL THEN
        RAISE EXCEPTION 'Message with ID % not found', p_id;
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_message(
    p_chat_id uuid,
    p_role text,
    p_content text DEFAULT NULL,
    p_content_analysis text DEFAULT NULL,
    p_content_comment text DEFAULT NULL,
    p_content_code text DEFAULT NULL,
    p_content_executable_code text DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_message_id uuid;
    v_message_createdAt timestamp with time zone;
    v_content_id uuid;
BEGIN
    -- Insertar los datos en la tabla messagesContent
    IF p_role = 'ai' THEN
        INSERT INTO public.messagesContent_ai(
            contentAnalysis,
            contentComment,
            contentCode,
            contentExecutableCode
        )
        VALUES (
            p_content_analysis,
            p_content_comment,
            p_content_code,
            p_content_executable_code
        )
        RETURNING id INTO v_content_id;
    ELSE
        INSERT INTO public.messagesContent_user(
            content
        )
        VALUES (
            p_content
        )
        RETURNING id INTO v_content_id;
    END IF;

    -- Verificar si se generó un ID para el contenido
    IF v_content_id IS NULL THEN
        RAISE EXCEPTION 'Failed to create message content';
    END IF;

    INSERT INTO public.messagesContent
    (
        id
    )
    VALUES (
        v_content_id
    );

    -- Insertar los datos en la tabla messages
    INSERT INTO public.messages(
        chatId,
        role,
        contentId
    )
    VALUES (
        p_chat_id,
        p_role,
        v_content_id
    )
    RETURNING id, createdAt INTO v_message_id, v_message_createdAt;

    -- Retornar el ID generado como JSON
    RETURN json_build_object('id', v_message_id, 'created_at', v_message_createdAt);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.delete_message(
    p_id uuid
)
RETURNS JSON AS $$
DECLARE
    deleted_id uuid;
BEGIN

    SELECT id FROM public.messages WHERE id = p_id INTO deleted_id;

    -- Check if any row was deleted
    IF deleted_id IS NULL THEN
        RAISE EXCEPTION 'Message with ID % not found', p_id;
    END IF;

    -- Delete the message record
    DELETE FROM public.messages
    WHERE id = p_id
    RETURNING id INTO deleted_id;


    RETURN json_build_object('id', deleted_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.delete_message_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Eliminar los registros relacionados en la tabla messagesContent
    IF OLD.role = 'ai' THEN
        DELETE FROM public.messagesContent_ai
        WHERE id = OLD.contentId;
    ELSE
        DELETE FROM public.messagesContent_user
        WHERE id = OLD.contentId;
    END IF;

    -- Eliminar los registros relacionados en la tabla attachments
    DELETE FROM public.attachments
    WHERE messageId = OLD.id;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_delete_message
AFTER DELETE ON public.messages
FOR EACH ROW
EXECUTE FUNCTION public.delete_message_trigger();

CREATE OR REPLACE FUNCTION public.get_all_attachments(
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.attachments;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'message_id', u.messageId,
                            'url', u.url,
                            'filename', u.filename,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.attachments u
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_attachment_by_id(
    p_id uuid
)
RETURNS json AS $$
BEGIN

    RETURN (
        SELECT
            json_build_object(
                'id', u.id,
                'message_id', u.messageId,
                'url', u.url,
                'filename', u.filename,
                'created_at', u.createdAt
            )
        FROM public.attachments u
        WHERE u.id = p_id
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_attachment(
    p_message_id uuid,
    p_url text,
    p_filename text
)
RETURNS JSON AS $$
DECLARE
    v_attachment_id uuid;
    v_attachment_createdAt timestamp with time zone;
BEGIN
    -- Insertar los datos en la tabla attachments
    INSERT INTO public.attachments(
        messageId,
        url,
        filename
    )
    VALUES (
        p_message_id,
        p_url,
        p_filename
    )
    RETURNING id, createdAt INTO v_attachment_id, v_attachment_createdAt;

    -- Retornar el ID generado como JSON
    RETURN json_build_object('id', v_attachment_id, 'created_at', v_attachment_createdAt);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.update_attachment(
    p_id uuid,
    p_url text DEFAULT NULL,
    p_filename text DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    updated_id uuid;
BEGIN
    -- Update the attachment record
    UPDATE public.attachments
    SET
        url = COALESCE(p_url, url),
        filename = COALESCE(p_filename, filename)
    WHERE id = p_id
    RETURNING id INTO updated_id;

    -- Check if any row was updated
    IF updated_id IS NULL THEN
        RAISE EXCEPTION 'Attachment with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', updated_id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.delete_attachment(
    p_id uuid
)
RETURNS JSON AS $$
DECLARE
    deleted_id uuid;
BEGIN
    -- Delete the attachment record
    DELETE FROM public.attachments
    WHERE id = p_id
    RETURNING id INTO deleted_id;

    -- Check if any row was deleted
    IF deleted_id IS NULL THEN
        RAISE EXCEPTION 'Attachment with ID % not found', p_id;
    END IF;

    RETURN json_build_object('id', deleted_id);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public.get_all_attachment_by_message_id(
    p_message_id uuid
)
RETURNS json AS $$
BEGIN
    RETURN (
        SELECT
            json_agg(
            json_build_object(
                'id', u.id,
                'url', u.url,
                'filename', u.filename,
                'created_at', u.createdAt
            )
            )
        FROM public.attachments u
        WHERE u.messageId = p_message_id
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_messages_with_content_attachment_by_chatId(
    p_chatId uuid,
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 1
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros filtrado por chatId
    SELECT COUNT(*) INTO v_total
    FROM public.messages
    WHERE chatId = p_chatId;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(message_data ORDER BY created_at DESC) AS messages
                    FROM (
                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                           'content', c.content
                                           ),
                                'attachments', (
                                    SELECT get_all_attachment_by_message_id(u.id)
                                )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_user c ON u.contentId = c.id
                        WHERE u.role = 'user' AND u.chatId = p_chatId

                        UNION ALL

                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                    'content_analysis', c.contentAnalysis,
                                    'content_comment', c.contentComment,
                                    'content_code', c.contentCode,
                                    'content_executable_code', c.contentExecutableCode
                                ),
                                'attachments', (
                                    SELECT get_all_attachment_by_message_id(u.id)
                                )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_ai c ON u.contentId = c.id
                        WHERE u.role = 'ai' AND u.chatId = p_chatId

                        ORDER BY created_at DESC
                        LIMIT p_limit OFFSET p_offset
                    ) subquery
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_full_messages_with_content_by_chatId(
    p_chatId uuid
)
RETURNS json AS $$
BEGIN
     RETURN (
        SELECT json_build_object(
            'data', COALESCE(
                (
                    SELECT json_agg(message_data ORDER BY created_at DESC) AS messages
                    FROM (
                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                           'content', c.content
                                           )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_user c ON u.contentId = c.id
                        WHERE u.role = 'user' AND u.chatId = p_chatId

                        UNION ALL

                        SELECT
                            json_build_object(
                                'id', u.id,
                                'chat_id', u.chatId,
                                'created_at', u.createdAt,
                                'role', u.role,
                                'content', json_build_object(
                                    'content_analysis', c.contentAnalysis,
                                    'content_comment', c.contentComment,
                                    'content_code', c.contentCode,
                                    'content_executable_code', c.contentExecutableCode
                                )
                            ) AS message_data,
                            u.createdAt AS created_at
                        FROM public.messages u
                        LEFT JOIN public.messagesContent_ai c ON u.contentId = c.id
                        WHERE u.role = 'ai' AND u.chatId = p_chatId
                        ORDER BY created_at
                    ) subquery
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_chats_by_user_id(
    p_user_id uuid,
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.chats WHERE userId = p_user_id;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'user_id', u.userId,
                            'scheme_id', u.schemeId,
                            'name_chat', u.nameChat,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.chats u
                    WHERE u.userId = p_user_id
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_schemes_by_user_id(
    p_user_id uuid,
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.schemes WHERE userId = p_user_id;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'title', u.title,
                            'content', u.content,
                            'attachment_url', u.attachmentUrl,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.schemes u
                    WHERE u.userId = p_user_id
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_chats_by_scheme_id(
    p_scheme_id uuid,
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.chats WHERE schemeId = p_scheme_id;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'user_id', u.userId,
                            'scheme_id', u.schemeId,
                            'name_chat', u.nameChat,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.chats u
                    WHERE u.schemeId = p_scheme_id
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_user_with_chats(
    p_user_id uuid
)
RETURNS json AS $$
DECLARE
    v_user json;
    v_chats json;
BEGIN
    -- Obtener el usuario
    v_user := public.get_user_by_id(p_user_id);

    -- Obtener los chats del usuario
    v_chats := public.get_all_chats_by_user_id(p_user_id);

    -- Retornar el objeto JSON con el usuario y sus chats
    RETURN json_build_object(
        'user', v_user,
        'chats', v_chats
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_all_schemes_by_chat_id(
    p_chat_id uuid,
    p_limit integer DEFAULT 100,
    p_offset integer DEFAULT 0
)
RETURNS json AS $$
DECLARE
    v_total integer;
BEGIN
    -- Obtener el total de registros
    SELECT COUNT(*) INTO v_total FROM public.schemes s
    INNER JOIN public.chats c on s.id = c.schemeId AND c.id = p_chat_id;

    -- Retornar objeto JSON con metadatos de paginación
    RETURN (
        SELECT json_build_object(
            'total', v_total,
            'limit', p_limit,
            'offset', p_offset,
            'pages', CEILING(v_total::numeric / p_limit),
            'data', COALESCE(
                (
                    SELECT json_agg(
                        json_build_object(
                            'id', u.id,
                            'title', u.title,
                            'content', u.content,
                            'attachment_url', u.attachmentUrl,
                            'created_at', u.createdAt
                        )
                    )
                    FROM public.schemes u
                    INNER JOIN public.chats c on u.id = c.schemeId AND c.id = p_chat_id
                    LIMIT p_limit OFFSET p_offset
                ),
                '[]'::json
            )
        )
    );
END;
$$ LANGUAGE plpgsql;