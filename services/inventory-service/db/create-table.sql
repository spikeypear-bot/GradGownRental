CREATE SCHEMA IF NOT EXISTS inventory_service;

SET search_path TO inventory_service;




CREATE TABLE InventoryStyle (
    style_id INT PRIMARY KEY,
    item_name VARCHAR(100),
    item_type VARCHAR(50),
    item_price DECIMAL (10,2),
    rental_fee DECIMAL (10,2),
    deposit DECIMAL (10,2)  
);
CREATE TABLE Inventory (
    model_id VARCHAR(50) PRIMARY KEY,
    style_id INT,
    size VARCHAR(50),
    total_qty INT,
    FOREIGN KEY (style_id) REFERENCES InventoryStyle(style_id)
);

CREATE TABLE Package(
    package_id SERIAL PRIMARY KEY,
    education_level VARCHAR(50),
    institution VARCHAR(100),
    faculty VARCHAR(100),
    hat_style_id INT,
    hood_style_id INT,
    gown_style_id INT,
    FOREIGN KEY (hat_style_id) REFERENCES InventoryStyle(style_id),
    FOREIGN KEY (hood_style_id) REFERENCES InventoryStyle(style_id),
    FOREIGN KEY (gown_style_id) REFERENCES InventoryStyle(style_id)
);

CREATE TABLE InventoryQuantityTrack (
    date DATE,
    model_id VARCHAR(50),
    available_qty INT DEFAULT 0,
    reserved_qty INT DEFAULT 0,
    rented_qty INT DEFAULT 0,
    damaged_qty INT DEFAULT 0,
    repair_qty INT DEFAULT 0,
    wash_qty INT DEFAULT 0,
    backup_qty INT DEFAULT 0,
    PRIMARY KEY (date, model_id),
    FOREIGN KEY (model_id) REFERENCES Inventory(model_id)
);

CREATE TABLE ItemHold (
    hold_id VARCHAR(50) NOT NULL,
    model_id VARCHAR(50) NOT NULL,
    qty INT,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (hold_id, model_id),
    FOREIGN KEY (model_id) REFERENCES Inventory(model_id)

);



ALTER TABLE InventoryQuantityTrack
ADD COLUMN IF NOT EXISTS available_qty INT DEFAULT 0;

ALTER TABLE InventoryQuantityTrack
ADD COLUMN IF NOT EXISTS damaged_qty INT DEFAULT 0;

ALTER TABLE InventoryQuantityTrack
ADD COLUMN IF NOT EXISTS repair_qty INT DEFAULT 0;

-- InventoryStyle

INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(1, 'Light Cerise Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(2, 'Golden Yellow with Gold Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(3, 'Light Cerise with White Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(4, 'Silver Grey with Gold Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(5, 'White Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(6, 'Tangerine Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(7, 'Orange Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(8, 'Russett Brown Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(9, 'Gold with White Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(10, 'Yellow Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(11, 'Medium Light Blue Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(12, 'Crimson Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(13, 'Lilac Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(14, 'Silver Grey with Crimson Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(15, 'Gold Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(16, 'Deep Gold Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(17, 'Lemon Yellow Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(18, 'Forest Green with Aquamarine Trim Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(19, 'Yale Blue with White Trim and Sash Hood', 'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(20, 'Dark Blue Gown with Distinguished Long Pointed Sleeves', 'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(21, 'Dark Blue Gown with Distinguished Long Pointed Sleeves and Crimson Trim', 'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(22, 'Yale Gown', 'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(23, 'Dark Blue Gown with Distinguished Elongated Sleeves', 'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(24, 'NUS Mortarboard with Black Tassel', 'hat', 15.0, 10.0, 5.0);
INSERT INTO InventoryStyle
(style_id, item_name, item_type, item_price, rental_fee, deposit)
VALUES
(25, 'Cotton Bonnet with a Cord and Tassel in Green', 'hat', 30.0, 20.0, 15.0);
INSERT INTO InventoryStyle 
(style_id, item_name, item_type,item_price,rental_fee,deposit) 
VALUES (26, 'Dark Blue Gown with Green Trimmings on the Front Panel and Bell Sleeves', 'gown',200.00, 100.00,80.00);
INSERT INTO InventoryStyle 
(style_id, item_name, item_type,item_price,rental_fee,deposit) 
VALUES (27, 'Hood Lined in Blue and Green Trimmed Edges', 'hood',45.0,20.0,30.0);

-- PACKAGES
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Arts', 24, 1, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Arts', 24, 1, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Applied Science', 24, 2, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Applied Science', 24, 2, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Arts (Industrial Design)', 24, 3, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Arts (Industrial Design)', 24, 3, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Landscape Architecture', 24, 3, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Landscape Architecture', 24, 3, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Arts (Architecture)', 24, 3, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Arts (Architecture)', 24, 3, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science (Project & Facilities Management)', 24, 4, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science (Project & Facilities Management)', 24, 4, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Business Administration', 24, 5, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Business Administration', 24, 5, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Computing', 24, 6, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Computing', 24, 6, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Social Science', 24, 7, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Social Science', 24, 7, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Dental Surgery', 24, 8, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Dental Surgery', 24, 8, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Engineering', 24, 9, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Engineering', 24, 9, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Technology', 24, 10, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Technology', 24, 10, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Laws', 24, 11, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Laws', 24, 11, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Medicine and Surgery', 24, 12, 21);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Medicine and Surgery', 24, 12, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science (Pharmacy)', 24, 13, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science (Pharmacy)', 24, 13, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science (Real Estate)', 24, 14, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science (Real Estate)', 24, 14, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science', 24, 15, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science', 24, 15, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Music', 24, 16, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Music', 24, 16, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science (Nursing)', 24, 17, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science (Nursing)', 24, 17, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Science (Nursing Practice)', 24, 17, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Science (Nursing Practice)', 24, 17, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Environmental Studies', 24, 18, 20);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Environmental Studies', 24, 18, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Bachelor', 'NUS', 'Yale', 24, 19, 22);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Masters', 'NUS', 'Yale', 24, 19, 23);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES
('Doctor', 'NUS', 'All Faculties', 25, 27, 26);




-- InventoryStyle Inserts

INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (28, 'Crimson edged with Gold Hood',  'hood', 27.25, 19.60, 18.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (29, 'Gold edged with White Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (30, 'Gold edged with Purple Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (31, 'Navy Blue edged with Light Green Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (32, 'Orange edged with Crimson Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (33, 'Alizarin Crimson edged with White and Magenta Hood',  'hood',19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (34, 'Crimson edged with White Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (35, 'Purple edged with Grey Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (36, 'Orange edged with White Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (37, 'Orange edged with Light Blue Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (38, 'Light Blue edged with Red and White Hood',  'hood',19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (39, 'Lustrous Light Cerise Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (40, 'Maroon edged with Black Hood',  'hood', 19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (41, 'Peacock Blue edged with Lustrous Gold Hood',  'hood',19.60, 16.35, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (42, 'Gown with Gold Front',  'gown', 54.50	,38.15	,35.00);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (43, 'Blue Gown with Sleeves',  'gown', 30.50,	19.60	,18.00);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (44, 'Gown with Crimson Front and Sleeves',  'gown', 30.50,	19.60	,18.00);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (45, 'Mortarboard',  'hat', 15.25,	10.90	,10.00);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (46, 'Bonnet',  'hat', 38.15	,27.25	,25.00);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (47, 'Purple Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (48, 'Golden Yellow Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (49, 'Drab with Golden Trimmings Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (50, 'Drab Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (51, 'Citron Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (52, 'Copper Hood',  'hood', 45.0, 20.0, 30.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (53, 'Black Mortarboard with Tassel',  'hat', 15.0, 10.0, 5.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (54, 'Black Bonnet with Gold Tassel',  'hat', 22.0, 15.0, 8.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (55, 'Black Gown with Pointed Sleeves',  'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (56, 'Black Gown with Oblong Sleeves',  'gown', 75.0, 40.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (57, 'Black Gown with Yellow Front and Sides',  'gown', 95.0, 63.0, 40.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (58, 'Gown Robe with Red-Yellow Flap',  'gown', 30.0, 20.0, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (59, 'Gown Robe with Red-Blue Flap',  'gown', 30.0, 20.0, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (60, 'Gown Robe with Red-Purple Flap',  'gown', 30.0, 20.0, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (61, 'Gown Robe with Gold Flap and Gold edges',  'gown', 40.0, 25.0, 20.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (62, 'Gown Robe with Red Front',  'gown', 40.0, 25.0, 15.0);
INSERT INTO InventoryStyle
(style_id, item_name,  item_type, item_price, rental_fee, deposit)
VALUES (63, 'Navy Blue Graduation Gown with Hood',  'gown', 40.0, 25.0, 15.0);


-- Package Inserts

INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'NTU', 'Philosophy', 46, 28, 44);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Master', 'NTU', 'Engineering', 45 ,29, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Engineering', 45, 29, 42);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Science', 45, 30, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Renaissance Engineering', 45, 30, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Science', 45, 31, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Business', 45, 32, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Arts', 45, 33, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Arts', 45, 34, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Medicine', 45, 35, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Accountancy', 45, 36, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Business', 45, 37, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Education (NIE)', 45, 38, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Education (NIE)', 45, 39, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Communication Studies', 45, 40, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Communication Studies', 45, 40, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'NTU', 'Social Sciences', 45, 41, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'NTU', 'Social Sciences', 45, 41, 43);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Law', 53, 47, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Law', 53, 47, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Law', 54, 47, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Science (Computer Science)', 53, 48, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Science (Information Systems)', 53, 48, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Science (Computing and Law)', 53, 48, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Information Technology in Business', 53, 48, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Engineering', 54, 48, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Computer Science', 54, 48, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Information Systems', 54, 48, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Accountancy', 53, 49, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Accountancy', 53, 49, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Accounting', 54, 49, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Business Management', 53, 50, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Business Management', 53, 50, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Business', 54, 50, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Social Science', 53, 51, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Sustainability', 53, 51, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Psychology', 54, 51, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Bachelor', 'SMU', 'Science (Economics)', 53, 52, 55);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Master', 'SMU', 'Science in Financial Economics',  53,52, 56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Doctor', 'SMU', 'Philosophy in Economics', 54, 52, 57);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Masters', 'SMU', 'Science in Financial Economics',53, 52,  56);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Nitec', 'ITE', 'Nitec', NULL,NULL,  58);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Higher Nitec', 'ITE', 'Higher Nitec',  NULL,NULL, 59);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Word-Study Diploma', 'ITE', 'Word-Study Diploma',NULL,NULL,   60);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Technical Diploma', 'ITE', 'Technical Diploma', NULL,NULL,  60);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Polytechnic Diploma', 'Singapore Polytechnic', 'Polytechnic Diploma', NULL,NULL,  61);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Polytechnic Diploma', 'Temasek Polytechnic', 'Polytechnic Diploma',  NULL,NULL, 62);
INSERT INTO Package
(education_level, institution, faculty, hat_style_id, hood_style_id, gown_style_id)
VALUES ('Polytechnic Diploma', 'Nanyang Polytechnic', 'Polytechnic Diploma', NULL,NULL,  63);

--Model

INSERT INTO Inventory (model_id, style_id, size, total_qty) VALUES
('0000001',1,'XS',250),
('0100001',1,'S',250),
('0200001',1,'M',250),
('0300001',1,'L',250),
('0400001',1,'XL',250),

('0000002',2,'XS',250),
('0100002',2,'S',250),
('0200002',2,'M',250),
('0300002',2,'L',250),
('0400002',2,'XL',250),

('0000003',3,'XS',250),
('0100003',3,'S',250),
('0200003',3,'M',250),
('0300003',3,'L',250),
('0400003',3,'XL',250),

('0000004',4,'XS',250),
('0100004',4,'S',250),
('0200004',4,'M',250),
('0300004',4,'L',250),
('0400004',4,'XL',250),

('0000005',5,'XS',250),
('0100005',5,'S',250),
('0200005',5,'M',250),
('0300005',5,'L',250),
('0400005',5,'XL',250),

('0000006',6,'XS',250),
('0100006',6,'S',250),
('0200006',6,'M',250),
('0300006',6,'L',250),
('0400006',6,'XL',250),

('0000007',7,'XS',250),
('0100007',7,'S',250),
('0200007',7,'M',250),
('0300007',7,'L',250),
('0400007',7,'XL',250),

('0000008',8,'XS',250),
('0100008',8,'S',250),
('0200008',8,'M',250),
('0300008',8,'L',250),
('0400008',8,'XL',250),

('0000009',9,'XS',250),
('0100009',9,'S',250),
('0200009',9,'M',250),
('0300009',9,'L',250),
('0400009',9,'XL',250),

('0000010',10,'XS',250),
('0100010',10,'S',250),
('0200010',10,'M',250),
('0300010',10,'L',250),
('0400010',10,'XL',250),

('0000011',11,'XS',250),
('0100011',11,'S',250),
('0200011',11,'M',250),
('0300011',11,'L',250),
('0400011',11,'XL',250),

('0000012',12,'XS',250),
('0100012',12,'S',250),
('0200012',12,'M',250),
('0300012',12,'L',250),
('0400012',12,'XL',250),

('0000013',13,'XS',250),
('0100013',13,'S',250),
('0200013',13,'M',250),
('0300013',13,'L',250),
('0400013',13,'XL',250),

('0000014',14,'XS',250),
('0100014',14,'S',250),
('0200014',14,'M',250),
('0300014',14,'L',250),
('0400014',14,'XL',250),

('0000015',15,'XS',250),
('0100015',15,'S',250),
('0200015',15,'M',250),
('0300015',15,'L',250),
('0400015',15,'XL',250),

('0000016',16,'XS',250),
('0100016',16,'S',250),
('0200016',16,'M',250),
('0300016',16,'L',250),
('0400016',16,'XL',250),

('0000017',17,'XS',250),
('0100017',17,'S',250),
('0200017',17,'M',250),
('0300017',17,'L',250),
('0400017',17,'XL',250),

('0000018',18,'XS',250),
('0100018',18,'S',250),
('0200018',18,'M',250),
('0300018',18,'L',250),
('0400018',18,'XL',250),

('0000019',19,'XS',250),
('0100019',19,'S',250),
('0200019',19,'M',250),
('0300019',19,'L',250),
('0400019',19,'XL',250),

('0000020',20,'XS',250),
('0100020',20,'S',250),
('0200020',20,'M',250),
('0300020',20,'L',250),
('0400020',20,'XL',250),

('0000021',21,'XS',250),
('0100021',21,'S',250),
('0200021',21,'M',250),
('0300021',21,'L',250),
('0400021',21,'XL',250),

('0000022',22,'XS',250),
('0100022',22,'S',250),
('0200022',22,'M',250),
('0300022',22,'L',250),
('0400022',22,'XL',250),

('0000023',23,'XS',250),
('0100023',23,'S',250),
('0200023',23,'M',250),
('0300023',23,'L',250),
('0400023',23,'XL',250),

('0000024',24,'XS',250),
('0100024',24,'S',250),
('0200024',24,'M',250),
('0300024',24,'L',250),
('0400024',24,'XL',250),

('0000025',25,'XS',250),
('0100025',25,'S',250),
('0200025',25,'M',250),
('0300025',25,'L',250),
('0400025',25,'XL',250),

('0000026',26,'XS',250),
('0100026',26,'S',250),
('0200026',26,'M',250),
('0300026',26,'L',250),
('0400026',26,'XL',250),

('0000027',27,'XS',250),
('0100027',27,'S',250),
('0200027',27,'M',250),
('0300027',27,'L',250),
('0400027',27,'XL',250);

INSERT INTO Inventory (model_id, style_id, size, total_qty) VALUES
('1000028',28,'XS',250),
('1100028',28,'S',250),
('1200028',28,'M',250),
('1300028',28,'L',250),
('1400028',28,'XL',250),

('1000029',29,'XS',250),
('1100029',29,'S',250),
('1200029',29,'M',250),
('1300029',29,'L',250),
('1400029',29,'XL',250),

('1000030',30,'XS',250),
('1100030',30,'S',250),
('1200030',30,'M',250),
('1300030',30,'L',250),
('1400030',30,'XL',250),

('1000031',31,'XS',250),
('1100031',31,'S',250),
('1200031',31,'M',250),
('1300031',31,'L',250),
('1400031',31,'XL',250),

('1000032',32,'XS',250),
('1100032',32,'S',250),
('1200032',32,'M',250),
('1300032',32,'L',250),
('1400032',32,'XL',250),

('1000033',33,'XS',250),
('1100033',33,'S',250),
('1200033',33,'M',250),
('1300033',33,'L',250),
('1400033',33,'XL',250),

('1000034',34,'XS',250),
('1100034',34,'S',250),
('1200034',34,'M',250),
('1300034',34,'L',250),
('1400034',34,'XL',250),

('1000035',35,'XS',250),
('1100035',35,'S',250),
('1200035',35,'M',250),
('1300035',35,'L',250),
('1400035',35,'XL',250),

('1000036',36,'XS',250),
('1100036',36,'S',250),
('1200036',36,'M',250),
('1300036',36,'L',250),
('1400036',36,'XL',250),

('1000037',37,'XS',250),
('1100037',37,'S',250),
('1200037',37,'M',250),
('1300037',37,'L',250),
('1400037',37,'XL',250),

('1000038',38,'XS',250),
('1100038',38,'S',250),
('1200038',38,'M',250),
('1300038',38,'L',250),
('1400038',38,'XL',250),

('1000039',39,'XS',250),
('1100039',39,'S',250),
('1200039',39,'M',250),
('1300039',39,'L',250),
('1400039',39,'XL',250),

('1000040',40,'XS',250),
('1100040',40,'S',250),
('1200040',40,'M',250),
('1300040',40,'L',250),
('1400040',40,'XL',250),

('1000041',41,'XS',250),
('1100041',41,'S',250),
('1200041',41,'M',250),
('1300041',41,'L',250),
('1400041',41,'XL',250),

('1000042',42,'XS',250),
('1100042',42,'S',250),
('1200042',42,'M',250),
('1300042',42,'L',250),
('1400042',42,'XL',250),

('1000043',43,'XS',250),
('1100043',43,'S',250),
('1200043',43,'M',250),
('1300043',43,'L',250),
('1400043',43,'XL',250),

('1000044',44,'XS',250),
('1100044',44,'S',250),
('1200044',44,'M',250),
('1300044',44,'L',250),
('1400044',44,'XL',250),

('1000045',45,'XS',250),
('1100045',45,'S',250),
('1200045',45,'M',250),
('1300045',45,'L',250),
('1400045',45,'XL',250),

('1000046',46,'XS',250),
('1100046',46,'S',250),
('1200046',46,'M',250),
('1300046',46,'L',250),
('1400046',46,'XL',250);

INSERT INTO Inventory (model_id, style_id, size, total_qty) VALUES
('2000047',47,'XS',250),
('2100047',47,'S',250),
('2200047',47,'M',250),
('2300047',47,'L',250),
('2400047',47,'XL',250),

('2000048',48,'XS',250),
('2100048',48,'S',250),
('2200048',48,'M',250),
('2300048',48,'L',250),
('2400048',48,'XL',250),

('2000049',49,'XS',250),
('2100049',49,'S',250),
('2200049',49,'M',250),
('2300049',49,'L',250),
('2400049',49,'XL',250),

('2000050',50,'XS',250),
('2100050',50,'S',250),
('2200050',50,'M',250),
('2300050',50,'L',250),
('2400050',50,'XL',250),

('2000051',51,'XS',250),
('2100051',51,'S',250),
('2200051',51,'M',250),
('2300051',51,'L',250),
('2400051',51,'XL',250),

('2000052',52,'XS',250),
('2100052',52,'S',250),
('2200052',52,'M',250),
('2300052',52,'L',250),
('2400052',52,'XL',250),

('2000053',53,'XS',250),
('2100053',53,'S',250),
('2200053',53,'M',250),
('2300053',53,'L',250),
('2400053',53,'XL',250),

('2000054',54,'XS',250),
('2100054',54,'S',250),
('2200054',54,'M',250),
('2300054',54,'L',250),
('2400054',54,'XL',250),

('2000055',55,'XS',250),
('2100055',55,'S',250),
('2200055',55,'M',250),
('2300055',55,'L',250),
('2400055',55,'XL',250),

('2000056',56,'XS',250),
('2100056',56,'S',250),
('2200056',56,'M',250),
('2300056',56,'L',250),
('2400056',56,'XL',250),

('2000057',57,'XS',250),
('2100057',57,'S',250),
('2200057',57,'M',250),
('2300057',57,'L',250),
('2400057',57,'XL',250),

('3000058',58,'XS',250),
('3100058',58,'S',250),
('3200058',58,'M',250),
('3300058',58,'L',250),
('3400058',58,'XL',250),

('3000059',59,'XS',250),
('3100059',59,'S',250),
('3200059',59,'M',250),
('3300059',59,'L',250),
('3400059',59,'XL',250),

('3000060',60,'XS',250),
('3100060',60,'S',250),
('3200060',60,'M',250),
('3300060',60,'L',250),
('3400060',60,'XL',250),

('4000061',61,'XS',250),
('4100061',61,'S',250),
('4200061',61,'M',250),
('4300061',61,'L',250),
('4400061',61,'XL',250),

('5000062',62,'XS',250),
('5100062',62,'S',250),
('5200062',62,'M',250),
('5300062',62,'L',250),
('5400062',62,'XL',250),

('5000063',63,'XS',250),
('5100063',63,'S',250),
('5200063',63,'M',250),
('5300063',63,'L',250),
('5400063',63,'XL',250);
