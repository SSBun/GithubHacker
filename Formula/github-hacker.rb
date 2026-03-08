class GithubHacker < Formula
  desc "CLI tool to manage multiple GitHub accounts for batch operations"
  homepage "https://github.com/SSBun/GithubHacker"
  url "https://github.com/SSBun/GithubHacker/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "75f9af1b47c5613b008647805794071f899bff722c180289f8d4c0f581da20f2"
  license "MIT"
  version "0.1.0"
  head "https://github.com/SSBun/GithubHacker.git", branch: "main"

  depends_on "python@3.12"

  def install
    system "python3.12", "-m", "pip", "install", ".", "-e"
  end

  test do
    system "github-hacker", "--help"
  end
end
