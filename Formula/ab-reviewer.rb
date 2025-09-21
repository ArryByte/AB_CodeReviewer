# Homebrew formula for AB Code Reviewer
class AbReviewer < Formula
  desc "Automated code review workflow with AI integration"
  homepage "https://github.com/ab-code-reviewer/ab-reviewer"
  url "https://github.com/ab-code-reviewer/ab-reviewer/archive/v0.1.0.tar.gz"
  sha256 "322ff6e0ec701724e1fe23b96457ec61257e0233a3c1134558807312133addd6"
  license "MIT"

  depends_on "python@3.8"

  def install
    system "python3", "-m", "pip", "install", *std_pip_args, "."
  end

  test do
    system "#{bin}/ab-reviewer", "--help"
  end
end
