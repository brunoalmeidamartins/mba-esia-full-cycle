from langchain_openai import ChatOpenAI

from search import search_prompt

model = ChatOpenAI(model="gpt-4.1-mini", temperature=0.1)
chain = search_prompt | model


def main():
    print("Bem-vindo ao chat de busca!")
    print("Digite 'exit' para sair do chat.\n")
    while True:
        print("=" * 50)
        question = input("Pergunta: ")
        if question.lower() == "exit":
            break
        result = chain.invoke({"question": f"{question}"})
        print(f"Resposta: {result.content}")
        print("=" * 50, "\n")
    print("Obrigado por usar o chat de busca!")


if __name__ == "__main__":
    main()
