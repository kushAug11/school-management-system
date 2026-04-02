create database if not exists greenleaf_db;
use greenleaf_db;

drop table if exists order_records;
drop table if exists staff_details;
drop table if exists plant_inventory;

create table staff_details(
    email varchar(50) primary key, 
    name varchar(30) not null,
    password varchar(20) not null
);

insert into staff_details values("flora.garden@leaf.com", "Flora Green", "Plant@123");
insert into staff_details values("root.admin@leaf.com", "Root Admin", "Admin#99");


CREATE TABLE plant_inventory (
    plant_id INT PRIMARY KEY AUTO_INCREMENT,
    plant_name VARCHAR(50) UNIQUE NOT NULL,
    stock_count INT NOT NULL,
    price INT NOT NULL,
    nursery_section VARCHAR(50) NOT NULL DEFAULT 'Main Greenhouse'
);

INSERT INTO plant_inventory(plant_name, stock_count, price, nursery_section) 
VALUES ("Snake Plant", 50, 450, "Indoor Oasis");
INSERT INTO plant_inventory(plant_name, stock_count, price, nursery_section) 
VALUES ("Monstera Deliciosa", 30, 1200, "Indoor Oasis");
INSERT INTO plant_inventory(plant_name, stock_count, price, nursery_section) 
VALUES ("Lavender", 100, 250, "Aromatic Alley");
INSERT INTO plant_inventory(plant_name, stock_count, price, nursery_section) 
VALUES ("Echeveria Succulent", 200, 150, "Desert Corner");
INSERT INTO plant_inventory(plant_name, stock_count, price, nursery_section) 
VALUES ("Bonsai Juniper", 15, 3500, "Zen Zone");

create table order_records(
    order_id int primary key auto_increment,
    email varchar(50), 
    plant_id int,
    quantity int not null,
    total_cost int not null,
    foreign key (email) references staff_details(email),
    foreign key (plant_id) references plant_inventory(plant_id)
);

insert into order_records(email, plant_id, quantity, total_cost) values("flora.garden@leaf.com", 1, 2, 900);
