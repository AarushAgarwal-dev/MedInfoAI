from app.db import SessionLocal, engine
from app.models import Medicine, Kendra, BlogPost

def seed():
    db = SessionLocal()
    # Medicines
    medicines = [
        Medicine(name="Paracetamol", generic="Acetaminophen", company="BrandA", price=10),
        Medicine(name="Ibuprofen", generic="Ibuprofen", company="BrandB", price=15),
        Medicine(name="Cetirizine", generic="Cetirizine", company="BrandC", price=8),
    ]
    for m in medicines:
        if not db.query(Medicine).filter_by(name=m.name, company=m.company).first():
            db.add(m)
    # Kendras
    kendras = [
        Kendra(name="Kendra 1", lat=28.6139, lng=77.2090),
        Kendra(name="Kendra 2", lat=28.7041, lng=77.1025),
    ]
    for k in kendras:
        if not db.query(Kendra).filter_by(name=k.name).first():
            db.add(k)
    # Blog Posts
    posts = [
        BlogPost(title="Why Generic Medicines Matter", content="Generics are as effective as branded medicines but cost less."),
        BlogPost(title="How to Find Affordable Medicines", content="Tips and resources for finding affordable medicines in India."),
    ]
    for p in posts:
        if not db.query(BlogPost).filter_by(title=p.title).first():
            db.add(p)
    db.commit()
    db.close()
    print("Seeded initial data.")

if __name__ == "__main__":
    seed() 