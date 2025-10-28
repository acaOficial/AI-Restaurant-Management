from agents.customer import customer
from agents.receptionist import receptionist

def main():
    print("Cliente pregunta...")
    q = customer()
    print("Cliente:", q, "\n")

    print("Recepcionista responde...")
    r = receptionist(q)
    print("Recepcionista:", r)

if __name__ == "__main__":
    main()
