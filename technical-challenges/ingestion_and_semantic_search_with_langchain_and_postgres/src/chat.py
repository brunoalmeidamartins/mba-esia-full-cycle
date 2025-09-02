from config import PROVIDER, get_chat
from search import search_prompt

# Mount chain
model = get_chat(PROVIDER)
chain = search_prompt | model


def main():
    print("Faça sua pergunta e veja a resposta!")
    print("Digite 'exit' para sair do chat.\n")
    while True:
        print("=" * 50)
        question = input("PERGUNTA: ")
        if question.lower() == "exit":
            break
        if not question:
            continue
        result = chain.invoke({"question": f"{question}"})
        if isinstance(result, str):
            answer = result
        else:
            answer = result.content
        print(f"RESPOSTA: {answer}")
        print("=" * 50, "\n")
    print("Obrigado!")


if __name__ == "__main__":
    main()
