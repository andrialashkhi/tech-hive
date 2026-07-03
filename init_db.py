from datetime import date

from werkzeug.security import generate_password_hash

from ext import app, db
from models import Product, User, Order

products = [
    Product(
        name="AJAZZ AK820 MAX",
        image="keyboard2.jpg",
        category="Keyboards",
        description="Premium TKL mechanical keyboard with a built-in display, RGB lighting, and smooth magnetic switches.",
        price=200,
        stock=14,
        featured=True,
    ),
    Product(
        name="K-60 RGB",
        image="keyboard1.jpg",
        category="Keyboards",
        description="Compact keyboard with RGB lighting and a clean gaming design.",
        price=150,
        stock=22,
        featured=False,
    ),
    Product(
        name="AULA F75 Pro Wireless",
        image="https://m.media-amazon.com/images/I/61MC8BK0w0L._AC_SL1500_.jpg",
        category="Keyboards",
        description="Compact 75% wireless keyboard with Bluetooth, 2.4GHz, and USB connectivity.",
        price=200,
        stock=3,
        featured=False,
    ),
    Product(
        name="X11 Wireless Mouse",
        image="x11mouse.jpg",
        category="Mice",
        description="Wireless gaming mouse with a minimal black design and smooth movement.",
        price=120,
        stock=18,
        featured=True,
    ),
    Product(
        name="Vortex Pro Mouse",
        image="https://upload.wikimedia.org/wikipedia/commons/f/f1/A_black_wireless_computer_mouse.jpg",
        category="Mice",
        description="Ultra-lightweight symmetrical mouse with a 26K DPI sensor built for competitive play.",
        price=95,
        stock=0,
        featured=False,
    ),
    Product(
        name="Swarm 7.1 Headset",
        image="https://upload.wikimedia.org/wikipedia/commons/6/6f/Sound_BlasterX_H5_Gaming_Headset.jpg",
        category="Headsets",
        description="Over-ear headset with 7.1 surround sound, a detachable mic, and memory-foam cushions.",
        price=180,
        stock=9,
        featured=True,
    ),
    Product(
        name="Comet Lite Headset",
        image="https://upload.wikimedia.org/wikipedia/commons/7/7a/RGB_gaming_headset_on_desk_with_ambient_lighting.jpg",
        category="Headsets",
        description="Lightweight wired headset tuned for footstep clarity and long-session comfort.",
        price=85,
        stock=27,
        featured=False,
    ),
    Product(
        name="Hex Deskpad XL",
        image="https://upload.wikimedia.org/wikipedia/commons/f/f7/Logitech_Red_mouse_on_a_mouse_pad.jpg",
        category="Accessories",
        description="900x400mm stitched-edge desk mat with a smooth surface built for pinpoint tracking.",
        price=45,
        stock=40,
        featured=False,
    ),
]

with app.app_context():
    db.drop_all()
    db.create_all()

    db.session.add_all(products)

    moderator = User(
        username="hivekeeper",
        email="moderator@techhive.demo",
        password_hash=generate_password_hash("HiveMod2026!"),
        birthday=date(1996, 4, 12),
        role="moderator",
    )
    demo_user = User(
        username="demoplayer",
        email="player@techhive.demo",
        password_hash=generate_password_hash("PlayHive2026!"),
        birthday=date(2001, 9, 3),
        role="user",
    )
    db.session.add_all([moderator, demo_user])
    db.session.commit()

    sample_order = Order(
        full_name=demo_user.username,
        product_id=products[0].id,
        user_id=demo_user.id,
        quantity=1,
        status="Shipped",
    )
    db.session.add(sample_order)
    db.session.commit()

    print("Database created and seeded successfully.")
    print("\nDemo accounts:")
    print("  Moderator -> moderator@techhive.demo / HiveMod2026!")
    print("  User      -> player@techhive.demo / PlayHive2026!")
