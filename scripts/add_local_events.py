from app import app, db
from models.event_models import LocalEvent
from datetime import datetime, timedelta

def add_bangladesh_events():
    with app.app_context():
        # Check if we already have events
        if LocalEvent.query.count() > 0:
            print("Events already exist in the database. Skipping...")
            return
        
        # Create sample events with Bangladesh-specific locations and themes
        sample_events = [
            {
                'title': 'Dhaka International Folk Fest',
                'description': 'Experience traditional folk music from Bangladesh and around the world in this 3-day festival.',
                'detailed_description': 'The Dhaka International Folk Fest brings together folk musicians from across Bangladesh and around the world for three days of performances, workshops, and cultural exchange. Held at the Army Stadium, this festival showcases the rich diversity of folk traditions with over 200 artists performing on multiple stages. Visitors can enjoy not only music but also traditional crafts exhibitions, folk dance performances, and authentic local food stalls. The festival aims to preserve and promote folk heritage while creating a platform for cultural dialogue between different traditions.',
                'location': 'Dhaka',
                'event_date': datetime.now() + timedelta(days=15),
                'event_type': 'Festival'
            },
            {
                'title': 'Chittagong Art Exhibition',
                'description': 'A showcase of contemporary Bangladeshi art featuring works from emerging and established artists.',
                'detailed_description': 'The Chittagong Art Exhibition is a prestigious showcase of contemporary Bangladeshi art, featuring over 100 works from both emerging talents and established masters. The exhibition spans various mediums including painting, sculpture, photography, and digital art, with a special focus on works that explore themes of national identity, environmental concerns, and social change. Guided tours are available daily, and several participating artists will conduct workshops and talks throughout the exhibition period. The event is hosted at the Chittagong Cultural Center, with proceeds supporting arts education programs in local schools.',
                'location': 'Chittagong',
                'event_date': datetime.now() + timedelta(days=10),
                'event_type': 'Exhibition'
            },
            {
                'title': 'Pohela Boishakh Concert',
                'description': 'Celebrate Bengali New Year with a special concert featuring popular Bangladeshi musicians.',
                'detailed_description': 'The Pohela Boishakh Concert is the largest Bengali New Year celebration in Dhaka, featuring performances by Bangladesh\'s most beloved musicians and bands. The concert includes both traditional folk songs and contemporary fusion music that celebrates Bengali culture and heritage. The event takes place at Ramna Park, where a specially constructed stage and sound system ensure an immersive experience for all attendees. Food stalls offering traditional Bengali New Year delicacies will be available throughout the venue. The concert concludes with a spectacular fireworks display at midnight to welcome the new Bengali year.',
                'location': 'Dhaka',
                'event_date': datetime.now() + timedelta(days=30),
                'event_type': 'Concert'
            },
            {
                'title': 'Sylhet Cultural Performance',
                'description': 'Traditional dance and music performances showcasing the rich cultural heritage of Sylhet region.',
                'detailed_description': 'The Sylhet Cultural Performance is a vibrant showcase of the unique cultural traditions of the Sylhet region. The event features performances of Manipuri dance, Baul music, and other traditional art forms indigenous to northeastern Bangladesh. Professional dance troupes and musicians from across the region will present carefully choreographed pieces that tell the stories and history of Sylhet. The performance takes place at the Sylhet Shilpakala Academy and includes an exhibition of traditional costumes, instruments, and handicrafts. This is an excellent opportunity to experience the distinctive cultural identity of the Sylhet region in a single evening.',
                'location': 'Sylhet',
                'event_date': datetime.now() + timedelta(days=5),
                'event_type': 'Performance'
            },
            {
                'title': 'Rangpur Photography Exhibition',
                'description': 'A collection of stunning photographs capturing the natural beauty and daily life in northern Bangladesh.',
                'detailed_description': 'The Rangpur Photography Exhibition presents the work of 30 photographers who have documented the landscapes, people, and daily life of northern Bangladesh. The exhibition is divided into three thematic sections: "Rural Landscapes," "Urban Transitions," and "Faces of the North." Each photograph is accompanied by detailed captions explaining the context and significance of the image. The exhibition aims to highlight both the natural beauty of the region and the social challenges faced by its communities. Visitors will have the opportunity to meet some of the photographers during scheduled sessions and participate in photography workshops on the weekends.',
                'location': 'Rangpur',
                'event_date': datetime.now() + timedelta(days=20),
                'event_type': 'Exhibition'
            },
            {
                'title': 'Baishakhi Mela',
                'description': 'Traditional fair celebrating Bengali New Year with cultural performances, crafts, and local food.',
                'detailed_description': 'Baishakhi Mela is a traditional fair celebrating the Bengali New Year with a vibrant array of cultural activities. The fair features folk music performances, traditional dance shows, and theatrical presentations throughout the day. Artisans from across Bangladesh set up stalls displaying and selling traditional handicrafts, textiles, and artwork. A major highlight is the food section, where visitors can sample regional specialties and seasonal treats that are traditionally enjoyed during the Bengali New Year celebrations. The fair also includes traditional games and competitions for visitors of all ages, making it a perfect family outing.',
                'location': 'Khulna',
                'event_date': datetime.now() + timedelta(days=25),
                'event_type': 'Festival'
            },
            {
                'title': 'Cox\'s Bazar Beach Festival',
                'description': 'Join us for a weekend of music, food, and fun at the longest natural sea beach in the world.',
                'detailed_description': 'The Cox\'s Bazar Beach Festival is an annual celebration that brings together local and international artists for performances right on the beach. Enjoy live music across multiple stages, sample delicious seafood from local vendors, and participate in beach games and competitions. The festival also features art installations made from recycled ocean waste to raise awareness about marine conservation. Suitable for families and groups of all ages, with special activities for children during daytime hours.',
                'location': 'Cox\'s Bazar',
                'event_date': datetime.now() + timedelta(days=45),
                'event_type': 'Festival'
            },
            {
                'title': 'Dhaka International Film Festival',
                'description': 'A celebration of cinema showcasing films from Bangladesh and around the world.',
                'detailed_description': 'The Dhaka International Film Festival features screenings of over 200 films from 60 countries. Special focus on South Asian cinema with dedicated showcases of Bangladeshi films, both classic and contemporary. Panel discussions with filmmakers, actors, and critics are scheduled throughout the festival. A highlight is the "Women Filmmakers" section, which celebrates female-directed films and addresses gender issues in cinema. Festival venues include Bangladesh National Museum, Central Public Library, and Alliance Française de Dhaka.',
                'location': 'Dhaka',
                'event_date': datetime.now() + timedelta(days=60),
                'event_type': 'Festival'
            },
            {
                'title': 'Rajshahi Silk Expo',
                'description': 'Exhibition and sale of Bangladesh\'s famous Rajshahi silk and traditional textiles.',
                'detailed_description': 'The Rajshahi Silk Expo celebrates the legendary Rajshahi silk, known for its exceptional quality and craftsmanship. The exhibition includes displays from over 50 weavers and silk producers, showcasing the entire silk-making process from cocoon to finished garment. Visitors can observe live demonstrations of traditional weaving techniques and participate in workshops on natural dyeing methods. Special focus on the revival of heritage motifs and patterns that reflect Bangladesh\'s cultural identity. The expo also features fashion shows highlighting contemporary designs using traditional Rajshahi silk.',
                'location': 'Rajshahi',
                'event_date': datetime.now() + timedelta(days=35),
                'event_type': 'Exhibition'
            },
            {
                'title': 'Sufi Music Night',
                'description': 'An evening of spiritual Sufi music performances by renowned Bangladeshi and international artists.',
                'detailed_description': 'The Sufi Music Night brings together the finest Sufi musicians and performers for an evening of spiritual and transcendental music. Featured artists include both traditional Baul singers from rural Bangladesh and contemporary Sufi fusion bands. The event takes place in the historic setting of Lalbagh Fort, creating a mystical atmosphere perfectly suited to the soul-stirring performances. The program includes qawwali performances, Sufi poetry recitations, and improvisational musical sessions that invite audience participation. This annual event has become a significant cultural highlight for both spiritual seekers and music enthusiasts.',
                'location': 'Dhaka',
                'event_date': datetime.now() + timedelta(days=18),
                'event_type': 'Concert'
            },
            {
                'title': 'Chittagong Hill Tracts Cultural Festival',
                'description': 'Celebration of the diverse indigenous cultures of the Chittagong Hill Tracts region.',
                'detailed_description': 'The Chittagong Hill Tracts Cultural Festival showcases the rich cultural heritage of the various indigenous communities living in the region, including the Chakma, Marma, Tripura, and Mro peoples. The three-day festival features traditional dance performances, music, handicrafts, and culinary specialties from each community. Visitors can participate in workshops on traditional bamboo crafts, weaving techniques, and indigenous musical instruments. A special exhibition of traditional attire and ornaments highlights the distinctive aesthetic traditions of each community. The festival aims to promote cultural understanding and preservation of indigenous heritage in Bangladesh.',
                'location': 'Rangamati',
                'event_date': datetime.now() + timedelta(days=50),
                'event_type': 'Festival'
            },
            {
                'title': 'Bangladesh Jazz & Blues Festival',
                'description': 'Two days of performances by leading jazz and blues musicians from Bangladesh and abroad.',
                'detailed_description': 'The Bangladesh Jazz & Blues Festival features an eclectic mix of traditional and contemporary jazz and blues performances. The festival brings together established international artists with emerging Bangladeshi talents, creating unique collaborative performances. Multiple stages offer continuous music throughout the weekend, from intimate acoustic sets to full big band performances. Special workshops and masterclasses are available for music students and enthusiasts to learn from visiting artists. The festival grounds also feature art installations, craft beer stations, and gourmet food options that complement the musical experience.',
                'location': 'Dhaka',
                'event_date': datetime.now() + timedelta(days=40),
                'event_type': 'Concert'
            }
        ]
        
        # Add events to database
        for event_data in sample_events:
            event = LocalEvent(**event_data)
            db.session.add(event)
        
        db.session.commit()
        print(f"Added {len(sample_events)} Bangladesh-specific events to the database")

if __name__ == "__main__":
    add_bangladesh_events()
